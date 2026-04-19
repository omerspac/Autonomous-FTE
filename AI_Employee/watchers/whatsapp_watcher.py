import time
import logging
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

from .base_watcher import BaseWatcher

logger = logging.getLogger(__name__)

KEYWORDS = ["urgent", "invoice", "payment", "help"]

class WhatsAppWatcher(BaseWatcher):
    def __init__(self, vault_path: Path, check_interval_seconds: int = 120):
        super().__init__(vault_path, check_interval_seconds)
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def _start_browser(self):
        if not self.page:
            self.playwright = sync_playwright().start()
            use_system_chrome = os.getenv("WHATSAPP_USE_SYSTEM_CHROME", "false").lower() == "true"
            use_chrome_profile = os.getenv("WHATSAPP_USE_CHROME_PROFILE", "false").lower() == "true"
            chrome_user_data_dir = os.getenv("WHATSAPP_CHROME_USER_DATA_DIR", "").strip()
            chrome_profile = os.getenv("WHATSAPP_CHROME_PROFILE", "Default").strip()

            if use_system_chrome and use_chrome_profile and chrome_user_data_dir:
                logger.info("Starting WhatsApp watcher using system Chrome profile...")
                user_data_path = Path(chrome_user_data_dir).expanduser()
                if not user_data_path.is_absolute():
                    user_data_path = (Path.cwd() / user_data_path).resolve()

                # If the user provided a profile directory path directly (e.g. .../User Data/Default),
                # normalize it to launch_persistent_context requirements.
                if user_data_path.name.lower().startswith("profile") or user_data_path.name == "Default":
                    chrome_profile = user_data_path.name
                    user_data_path = user_data_path.parent

                if chrome_profile.lower() == "any":
                    candidates = []
                    if (user_data_path / "Default").exists():
                        candidates.append("Default")
                    for i in range(1, 11):
                        profile_name = f"Profile {i}"
                        if (user_data_path / profile_name).exists():
                            candidates.append(profile_name)
                    if not candidates:
                        candidates = ["Default"]

                    last_error = None
                    for candidate in candidates:
                        try:
                            logger.info(f"Trying Chrome profile: {candidate}")
                            self.context = self.playwright.chromium.launch_persistent_context(
                                user_data_dir=str(user_data_path),
                                channel="chrome",
                                headless=False,
                                args=[f"--profile-directory={candidate}"]
                            )
                            break
                        except Exception as e:
                            last_error = e
                            logger.warning(f"Chrome profile {candidate} unavailable: {e}")

                    if not self.context and last_error:
                        logger.warning(
                            "Could not attach to any existing Chrome profile. "
                            "Falling back to system Chrome regular mode."
                        )
                        logger.warning(f"Profile attach error: {last_error}")
                        self.browser = self.playwright.chromium.launch(channel="chrome", headless=False)
                        self.context = self.browser.new_context(
                            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
                        )
                else:
                    # Uses installed Chrome + persistent profile directory.
                    try:
                        self.context = self.playwright.chromium.launch_persistent_context(
                            user_data_dir=str(user_data_path),
                            channel="chrome",
                            headless=False,
                            args=[f"--profile-directory={chrome_profile}"]
                        )
                    except Exception as e:
                        logger.warning(
                            "Could not attach to the requested Chrome profile. "
                            "Falling back to system Chrome regular mode."
                        )
                        logger.warning(f"Profile attach error: {e}")
                        self.browser = self.playwright.chromium.launch(channel="chrome", headless=False)
                        self.context = self.browser.new_context(
                            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
                        )

                self.page = self.context.new_page()
            elif use_system_chrome:
                logger.info("Starting WhatsApp watcher using system Chrome (regular mode)...")
                self.browser = self.playwright.chromium.launch(channel="chrome", headless=False)
                self.context = self.browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
                )
                self.page = self.context.new_page()
            else:
                logger.info("Starting WhatsApp watcher using Playwright bundled Chromium...")
                self.browser = self.playwright.chromium.launch(headless=False)  # Headless=False to scan QR code
                self.context = self.browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
                )
                self.page = self.context.new_page()

            self.page.goto("https://web.whatsapp.com")
            logger.info("Waiting for WhatsApp Web login (Scan QR code)...")
            # Wait for specific element that appears after login
            try:
                self.page.wait_for_selector('div[data-testid="chat-list"]', timeout=60000)
                logger.info("WhatsApp Web login successful.")
            except Exception as e:
                logger.error("WhatsApp login timeout.")

    def check_for_updates(self) -> bool:
        if not self.page:
            self._start_browser()
            return False

        logger.debug("Checking for new WhatsApp messages...")
        try:
            # Look for chats with unread markers
            unread_chats = self.page.query_selector_all('span[aria-label*="unread message"]')
            
            if not unread_chats:
                return False

            new_processed = False
            for unread in unread_chats:
                chat_item = unread.query_selector('xpath=ancestor::div[@role="listitem"]')
                if not chat_item:
                    continue

                # Get chat name and last message snippet
                title_elem = chat_item.query_selector('span[title]')
                chat_name = title_elem.get_attribute('title') if title_elem else "Unknown Contact"
                
                # Check snippet for keywords
                snippet_elem = chat_item.query_selector('span[data-testid="last-msg-status"]')
                snippet = snippet_elem.inner_text().lower() if snippet_elem else ""

                if any(kw in snippet for kw in KEYWORDS):
                    item_id = f"{chat_name}_{int(time.time())}" # Simple unique ID
                    if self.is_processed(item_id):
                        continue

                    logger.info(f"Urgent WhatsApp message from {chat_name}: {snippet}")
                    
                    metadata = {
                        "type": "whatsapp",
                        "from": chat_name,
                        "priority": "urgent" if "urgent" in snippet else "normal",
                        "snippet": snippet,
                        "received": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    content = f"# WhatsApp Message from {chat_name}\n\n**Received:** {metadata['received']}\n\n**Message Preview:**\n> {snippet}\n\n---"
                    
                    self.create_action_file(metadata, content, "whatsapp")
                    self.mark_as_processed(item_id)
                    new_processed = True
                
            return new_processed

        except Exception as e:
            logger.error(f"WhatsApp automation error: {e}")
            if "launch_persistent_context" in str(e):
                logger.error("System Chrome launch failed. Close all Chrome windows for that profile, or set WHATSAPP_CHROME_USER_DATA_DIR to a dedicated folder.")
            # Recover on closed/invalid browser context and retry on next cycle.
            self.page = None
            self.context = None
            self.browser = None
            self.playwright = None
            return False

    def stop(self) -> None:
        super().stop()
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            logger.warning(f"Ignoring WhatsApp watcher shutdown error: {e}")
