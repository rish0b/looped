import requests
from .utils import setup_logger

class Webhook:
    def __init__(self, handler, silent=False):
        self.logger = setup_logger(silent)
        self.handler = handler
    
    def register_webhook(self, callback_url, message_id):
        response = self.handler.register_webhook(callback_url, message_id)
        self.logger.info(f"Webhook registration response: {response}")
        return response