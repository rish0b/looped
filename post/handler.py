from abc import ABC, abstractmethod

class Handler(ABC):
    """Handler interface that all service handlers must implement."""
    
    @abstractmethod
    def send_message(self, body):
        """Send a specific message."""
        pass

    @abstractmethod
    def check_for_feedback(self, message_id):
        """Check for feedback related to a specific message."""
        pass
    
    @abstractmethod
    def register_webhook(self, callback_url, message_id):
        """Register a webhook to listen for events."""
        pass