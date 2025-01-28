import requests
import aiohttp
from auth_manager import AuthManager
from handler import Handler
from utils import setup_logger
from config import (
    OUTLOOK_CLIENT_ID,
    OUTLOOK_CLIENT_SECRET,
    OUTLOOK_ACCESS_TOKEN
)
from constants import (
    OUTLOOK_TOKEN_URL,
    OUTLOOK_SCOPE_URL,
    OUTLOOK_SEND_MAIL_ENDPOINT,
    OUTLOOK_MESSAGES_ENDPOINT,
    OUTLOOK_SUBSCRIPTIONS_ENDPOINT
)

class Outlook(AuthManager, Handler):

    def __init__(self, client_id=OUTLOOK_CLIENT_ID, client_secret=OUTLOOK_CLIENT_SECRET, access_token=OUTLOOK_ACCESS_TOKEN, silent=False):
        super().__init__(access_token=access_token)
        self.logger = setup_logger(silent)
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json"
        }

    def _build_attachments(self, attachments):
        # Prepare attachments in the format expected by Outlook API
        attachment_objects = []
        for attachment in attachments:
            attachment_objects.append({
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": attachment['name'],
                "contentBytes": attachment['content_base64']
            })
        return attachment_objects

    def send_message(self, subject, body, to_email, attachments=None, adaptive_card=None):
        data = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "Text" if not adaptive_card else "HTML",
                    "content": body if not adaptive_card else adaptive_card
                },
                "toRecipients": [{"emailAddress": {"address": to_email}}]
            }
        }

        # Add attachments if any
        if attachments:
            data["message"]["attachments"] = self._build_attachments(attachments)

        # Send request
        response = requests.post(OUTLOOK_SEND_MAIL_ENDPOINT, json=data, headers=self._get_headers())
        response.raise_for_status()
        email_id = response.json().get("id")
        self.logger.info(f"Email sent with ID: {email_id}")
        return email_id

    async def send_message_async(self, subject, body, to_email, attachments=None, adaptive_card=None):
        data = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "Text" if not adaptive_card else "HTML",
                    "content": body if not adaptive_card else adaptive_card
                },
                "toRecipients": [{"emailAddress": {"address": to_email}}]
            }
        }

        # Add attachments if any
        if attachments:
            data["message"]["attachments"] = self._build_attachments(attachments)

        # Send request asynchronously
        async with aiohttp.ClientSession() as session:
            async with session.post(OUTLOOK_SEND_MAIL_ENDPOINT, json=data, headers=self._get_headers()) as response:
                response.raise_for_status()
                email_id = (await response.json()).get("id")
                self.logger.info(f"Email sent with ID: {email_id}")
                return email_id

    def check_for_feedback(self, message_id):
        response = requests.get(f"{OUTLOOK_MESSAGES_ENDPOINT}/{message_id}", headers=self._get_headers())
        response.raise_for_status()
        message_data = response.json()
        feedback = message_data.get("body", {}).get("content")
        attachments = message_data.get("attachments", [])
        
        self.logger.info(f"Feedback and attachments retrieved for message ID {message_id}")
        
        # Return both feedback and attachments
        return feedback, attachments

    async def check_for_feedback_async(self, message_id):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{OUTLOOK_MESSAGES_ENDPOINT}/{message_id}", headers=self._get_headers()) as response:
                response.raise_for_status()
                message_data = await response.json()
                feedback = message_data.get("body", {}).get("content")
                attachments = message_data.get("attachments", [])
                
                self.logger.info(f"Feedback and attachments retrieved for message ID {message_id}")
                
                # Return both feedback and attachments
                return feedback, attachments

    def register_webhook(self, callback_url, resource):
        data = {
            "changeType": "created",
            "notificationUrl": callback_url,
            "resource": resource,
            "expirationDateTime": "2025-12-31T23:59:59.999Z"
        }

        response = requests.post(OUTLOOK_SUBSCRIPTIONS_ENDPOINT, json=data, headers=self._get_headers())
        response.raise_for_status()
        webhook_id = response.json().get("id")
        self.logger.info(f"Webhook registered with ID: {webhook_id}")
        return webhook_id

    def authenticate(self):
        if self.is_token_valid():
            return

        if self.client_id and self.client_secret:
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": OUTLOOK_SCOPE_URL
            }
            response = requests.post(OUTLOOK_TOKEN_URL, data=data)
            response.raise_for_status()
            result = response.json()
            self.store_token(result["access_token"], result["expires_in"])
        else:
            raise Exception("Missing required credentials for Outlook")