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
        self.max_buffer_size = 100  # Keep buffer small for performance

    def process_key(
        self, char: str, is_backspace: bool = False
    ) -> Optional[Tuple[int, str, int]]:
        """
        Process a key event.
        Returns: (backspaces_to_delete_abbr, expansion_text, cursor_left_moves) or None
        """
        logger.debug(f"process_key called with char={repr(char)}, is_backspace={is_backspace}")

        if is_backspace:
            if self.buffer:
                self.buffer = self.buffer[:-1]
            logger.debug(f"Buffer after backspace: '{self.buffer}'")
            return None

        # Append char to buffer
        if char:
            self.buffer += char
            if len(self.buffer) > self.max_buffer_size:
                self.buffer = self.buffer[-self.max_buffer_size :]

        logger.info(f"Buffer before match: '{self.buffer}'")

        # Map last char (if any) to trigger
        trigger_map = {
            " ": TriggerType.SPACE,
            "\r": TriggerType.ENTER,
            "\n": TriggerType.ENTER,
        }
        trigger = trigger_map.get(char) if char else None

        potential_abbr = self.buffer
        if trigger:
            # Remove the trigger char to get the abbreviation candidate
            potential_abbr = self.buffer[:-1]

        logger.debug(
            f"Trigger={trigger}, potential_abbr='{potential_abbr}' "
            f"(full buffer='{self.buffer}')"
        )

        # Iterate through snippets to find a match at the end of the buffer
        for snippet in self.store.snippets:
            if not snippet.is_active:
                continue

            abbr = snippet.abbreviation
            match_condition = False

            if snippet.trigger == TriggerType.NONE:
                if self.buffer.endswith(abbr):
                    match_condition = True
            elif trigger and snippet.trigger == trigger:
                if potential_abbr.endswith(abbr):
                    match_condition = True

            logger.debug(
                f"Checking snippet id={snippet.id}, abbr='{abbr}', "
                f"trigger={snippet.trigger}, match={match_condition}"
            )

            if match_condition:
                logger.info(f"Match found: {abbr} -> {snippet.expansion}")
                logger.debug(
                    f"Matched abbreviation '{abbr}' -> expansion length={len(snippet.expansion)}"
                )

                # Resolve placeholders
                expanded_text = self.resolver.resolve(snippet.expansion)
                cursor_offset = self.resolver.get_cursor_offset(snippet.expansion)
                final_text = expanded_text.replace("{{cursor}}", "")

                # Calculate backspaces needed (abbr + trigger if any)
                chars_to_delete = len(abbr)
                if snippet.trigger != TriggerType.NONE:
                    chars_to_delete += 1

                # Clear buffer (simplest/safest for now)
                self.buffer = ""

                logger.info(
                    f"Expansion result: delete={chars_to_delete}, "
                    f"text='{final_text}', cursor_offset={cursor_offset}"
                )

                return (chars_to_delete, final_text, cursor_offset)

        logger.debug("No match found for current buffer.")
        return None
