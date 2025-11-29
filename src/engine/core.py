import logging
from typing import Optional, Tuple
from src.common.models import Snippet, TriggerType
from src.engine.store import Store
from src.engine.placeholders import PlaceholderResolver

logger = logging.getLogger(__name__)

class ExpansionEngine:
    def __init__(self, store: Store):
        self.store = store
        self.resolver = PlaceholderResolver()
        self.buffer = ""
        self.max_buffer_size = 100 # Keep buffer small for performance

    def process_key(self, char: str, is_backspace: bool = False) -> Optional[Tuple[int, str, int]]:
        """
        Process a key event.
        Returns: (backspaces_to_delete_abbr, expansion_text, cursor_left_moves) or None
        """
        if is_backspace:
            self.buffer = self.buffer[:-1]
            return None

        # Append char to buffer
        self.buffer += char
        if len(self.buffer) > self.max_buffer_size:
            self.buffer = self.buffer[-self.max_buffer_size:]

        # Check for matches
        # We check from longest possible match to shortest
        # But first, we need to handle triggers.
        
        # If the last char is a trigger (space/enter), we check the word before it.
        trigger_map = {" ": TriggerType.SPACE, "\r": TriggerType.ENTER, "\n": TriggerType.ENTER}
        trigger = trigger_map.get(char)

        potential_abbr = self.buffer
        if trigger:
             # Remove the trigger char to get the abbreviation candidate
            potential_abbr = self.buffer[:-1]

        # Iterate through snippets to find a match at the end of the buffer
        # This is O(N) where N is number of snippets. For v1 this is fine.
        # Optimization: Use a Trie or Reverse Map.
        
        for snippet in self.store.snippets:
            if not snippet.is_active:
                continue
            
            abbr = snippet.abbreviation
            
            # Check if buffer ends with this abbreviation
            match_condition = False
            
            if snippet.trigger == TriggerType.NONE:
                # Instant expansion: buffer ends with abbr
                if self.buffer.endswith(abbr):
                    match_condition = True
            elif trigger and snippet.trigger == trigger:
                # Triggered expansion: buffer ends with abbr + trigger
                # potential_abbr is buffer without trigger
                if potential_abbr.endswith(abbr):
                    match_condition = True

            if match_condition:
                logger.info(f"Match found: {abbr} -> {snippet.expansion}")
                
                # Resolve placeholders
                expanded_text = self.resolver.resolve(snippet.expansion)
                cursor_offset = self.resolver.get_cursor_offset(snippet.expansion)
                final_text = expanded_text.replace("{{cursor}}", "")
                
                # Calculate backspaces needed
                # We need to delete the abbreviation AND the trigger (if any)
                # But wait, if it's a trigger, the user typed it, so we delete it too?
                # Usually yes. e.g. "btw " -> "by the way "
                
                chars_to_delete = len(abbr)
                if snippet.trigger != TriggerType.NONE:
                    chars_to_delete += 1 # The trigger char
                
                # Reset buffer partially or fully? 
                # Safer to clear buffer or remove the used part.
                self.buffer = "" 
                
                return (chars_to_delete, final_text, cursor_offset)

        return None
