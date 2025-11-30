    def _handle_backend_message(self, msg):
        msg_type = msg.get("type")
        payload = msg.get("payload", {})

        if msg_type == MSG_REPLACE_TEXT:
            backspaces = payload.get("backspaces", 0)
            text = payload.get("text", "")
            cursor_offset = payload.get("cursor_offset", 0)

            logger.info(
                f"Replacing: backspaces={backspaces}, text='{text}', cursor_offset={cursor_offset}"
            )

            # 1) Delete abbreviation + trigger
            self.win32.send_backspace(backspaces)

            # 2) Clipboard-based insertion for reliability
            try:
                import pyperclip

                old_clip = None
                try:
                    old_clip = pyperclip.paste()
                except Exception:
                    old_clip = None

                pyperclip.copy(text)
                logger.info("Clipboard set; sending Ctrl+V")
                self.win32.send_ctrl_v()

                # (Optional) restore clipboard
                if old_clip is not None:
                    try:
                        pyperclip.copy(old_clip)
                    except Exception:
                        pass
            except Exception as e:
                logger.error(f"Clipboard-based insertion failed: {e}")
                # Fallback to direct key injection if needed
                self.win32.send_text(text)

            # 3) Cursor offset (move left if needed)
            if cursor_offset > 0:
                for _ in range(cursor_offset):
                    self.win32._send_key(0x25)  # VK_LEFT
