import os
import logging
import base64
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .base_watcher import BaseWatcher

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path: Path, check_interval_seconds: int = 300):
        super().__init__(vault_path, check_interval_seconds)
        self.enabled = True
        self.creds = None
        self.service = None
        try:
            self.creds = self._authenticate()
            self.service = build('gmail', 'v1', credentials=self.creds)
        except Exception as e:
            self.enabled = False
            logger.error(f"GmailWatcher disabled due to auth/setup error: {e}")

    def _authenticate(self):
        creds = None
        token_path = self.vault_path / "Logs" / "token.json"
        creds_path = Path("credentials.json") # Should be in root

        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not creds_path.exists():
                    logger.error("credentials.json not found. Please follow Gmail API setup.")
                    raise FileNotFoundError("credentials.json required for GmailWatcher.")
                flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        return creds

    def check_for_updates(self) -> bool:
        if not self.enabled or not self.service:
            return False

        logger.debug("Checking for new emails...")
        try:
            # Query for unread and important messages
            query = "is:unread is:important"
            results = self.service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])

            if not messages:
                return False

            new_processed = False
            for msg in messages:
                msg_id = msg['id']
                if self.is_processed(msg_id):
                    continue

                # Fetch full message
                message = self.service.users().messages().get(userId='me', id=msg_id).execute()
                payload = message.get('payload', {})
                headers = payload.get('headers', [])
                
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), "No Subject")
                sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), "Unknown Sender")
                received = next((h['value'] for h in headers if h['name'].lower() == 'date'), "Unknown Date")
                
                body = self._get_body(payload)
                
                metadata = {
                    "type": "email",
                    "from": sender,
                    "subject": subject,
                    "priority": "high", # is:important implies high
                    "received": received,
                    "msg_id": msg_id
                }
                
                content = f"# {subject}\n\n**From:** {sender}\n**Date:** {received}\n\n---\n\n{body}"
                
                self.create_action_file(metadata, content, "email")
                self.mark_as_processed(msg_id)
                new_processed = True
                
                # Optional: Mark as read or remove 'important' label if desired
                # self.service.users().messages().batchModify(userId='me', body={'ids': [msg_id], 'removeLabelIds': ['UNREAD']}).execute()

            return new_processed

        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            return False

    def _get_body(self, payload):
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        return base64.urlsafe_b64decode(data).decode('utf-8')
        else:
            data = payload.get('body', {}).get('data')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8')
        return "No text content found."
