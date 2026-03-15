import time
import logging
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
            self.browser = self.playwright.chromium.launch(headless=False) # Headless=False to scan QR code
            self.context = self.browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
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
            return False

    def stop(self) -> None:
        super().stop()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
