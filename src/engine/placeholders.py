import datetime
import pyperclip
import logging

logger = logging.getLogger(__name__)

class PlaceholderResolver:
    def resolve(self, text: str) -> str:
        """
        Replaces placeholders in the text with their actual values.
        Supported: {{date}}, {{time}}, {{datetime}}, {{clipboard}}, {{cursor}} (handled by engine)
        """
        now = datetime.datetime.now()
        
        # Date/Time
        text = text.replace("{{date}}", now.strftime("%Y-%m-%d"))
        text = text.replace("{{time}}", now.strftime("%H:%M"))
        text = text.replace("{{datetime}}", now.strftime("%Y-%m-%d %H:%M"))
        
        # Clipboard
        if "{{clipboard}}" in text:
            try:
                clipboard_content = pyperclip.paste()
                text = text.replace("{{clipboard}}", clipboard_content)
            except Exception as e:
                logger.error(f"Clipboard access failed: {e}")
                text = text.replace("{{clipboard}}", "")

        # {{cursor}} is special, it marks where the cursor should end up.
        # It is NOT replaced here, but handled by the engine to calculate backspaces/arrow keys.
        
        return text

    def get_cursor_offset(self, text: str) -> int:
        """
        Returns the number of characters from the END of the string to where the cursor should be.
        Removes {{cursor}} from the text.
        """
        if "{{cursor}}" not in text:
            return 0
        
        parts = text.split("{{cursor}}")
        # The cursor should be after the first part.
        # We need to know how many chars to move LEFT from the end of the final string.
        final_text = text.replace("{{cursor}}", "")
        
        # Length of text AFTER the cursor marker
        suffix_len = len(parts[1]) if len(parts) > 1 else 0
        return suffix_len
