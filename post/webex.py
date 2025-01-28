import requests
from auth_manager import AuthManager
from handler import Handler
from utils import setup_logger
from config import WEBEX_ACCESS_TOKEN

class Webex(AuthManager, Handler):
    # Constants for Webex
    WEBEX_API_URL = "https://webexapis.com/v1/messages"
    WEBEX_WEBHOOK_URL = "https://webexapis.com/v1/webhooks"
    
    def __init__(self, silent=False):
        self.logger = setup_logger(silent)
        self.access_token = WEBEX_ACCESS_TOKEN
    
    def send_message(self, text, to_email):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        data = {
            "roomId": "your_room_id",  # Change as per your setup
            "text": text
        }
        
        response = requests.post(self.WEBEX_API_URL, json=data, headers=headers)
        response.raise_for_status()
        message_id = response.json().get("id")
        
        self.logger.info(f"Message sent with ID: {message_id}")
        return message_id
    
    async def check_for_feedback(self, message_id):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(f"{self.WEBEX_API_URL}/{message_id}", headers=headers)
        response.raise_for_status()
        return response.json().get("text")
    
    def register_webhook(self, callback_url, message_id):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        data = {
            "targetUrl": callback_url,
            "resource": f"/messages/{message_id}",
            "event": "created"
        }
        
        response = requests.post(self.WEBEX_WEBHOOK_URL, json=data, headers=headers)
        response.raise_for_status()
        self.logger.info(f"Webhook registered with ID: {response.json().get('id')}")
        return response.json()
