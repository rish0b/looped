from .utils import setup_logger
from .config import WEBEX_ACCESS_TOKEN
from typing import Dict, Any, Optional
from webexteamssdk import WebexTeamsAPI


class Webex:

    def __init__(self, access_token=None):
        """Initialize Webex SDK with an access token."""
        # Use the provided access_token or the default from environment
        if access_token is None:
            access_token = WEBEX_ACCESS_TOKEN
        
        # Verify that access_token is not None or empty
        if not access_token:
            raise ValueError("Webex access token is required but was not provided.")
        
        self.api = WebexTeamsAPI(access_token=access_token)    

    def send_message(self, room_id: str, text: str, to_person_id: Optional[str] = None, to_person_email: Optional[str] = None) -> Dict[str, str]:
        """
        Send a text message to a Webex room (or direct message to a user or an email).
        If `to_person_email` is provided, it will send the message to the Webex user linked to that email.
        """
        if to_person_email:
            message = self.api.messages.create(text=text, toPersonEmail=to_person_email)
        elif to_person_id:
            message = self.api.messages.create(text=text, toPersonId=to_person_id)    
        else:
            message = self.api.messages.create(text=text, roomId=room_id)

        return {"message_id": message.id, "room_id": room_id}

    def send_card(self, room_id: str, card: Dict[str, Any], to_person_id: Optional[str] = None, to_person_email: Optional[str] = None) -> Dict[str, Any]:
        """
        Send an adaptive card to a Webex room (or direct message to a user or an email).
        If `to_person_email` is provided, it will send the card to the Webex user linked to that email.
        """
        if to_person_email:
            message = self.api.messages.create(
                toPersonEmail=to_person_email, 
                text="TESTING THE CARD",
                attachments=[{"contentType": "application/vnd.microsoft.card.adaptive", "content": card}]
            )
        elif to_person_id:
            message = self.api.messages.create(
                toPersonId=to_person_id, 
                text="TESTING THE CARD",
                attachments=[{"contentType": "application/vnd.microsoft.card.adaptive", "content": card}]
            )
        else:
            message = self.api.messages.create(
                roomId=room_id, 
                text="TESTING THE CARD",
                attachments=[{"contentType": "application/vnd.microsoft.card.adaptive", "content": card}]
            )    
        
        # Return card details along with message_id and room_id for future retrieval
        return {"message_id": message.id, "room_id": room_id, "action_ids": self.extract_action_ids(card)}

    def extract_action_ids(self, card: Dict[str, Any]) -> Optional[list]:
        """Extract action_ids from an adaptive card (if present)."""
        return [action["id"] for action in card.get("actions", [])] if card.get("actions") else []

    def handle_webhook_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming webhook event and return relevant details.
        - For card responses, return the action details and inputs.
        - For message events, return message and user details.
        """
        resource = event_data.get("resource")
        event = event_data.get("event")
        data = event_data.get("data")

        if resource == "messages" and event == "attachmentAction":
            # Card response
            action_data = data.get("data", {})
            message_id = action_data.get("messageId")
            room_id = action_data.get("roomId")
            user_id = action_data.get("actorId")
            action_inputs = action_data.get("inputs", {})
            action_id = action_data.get("id")

            return {
                "type": "card_response",
                "message_id": message_id,
                "room_id": room_id,
                "user_id": user_id,
                "action_id": action_id,
                "inputs": action_inputs
            }

        elif resource == "messages" and event == "created":
            # Message event
            message_id = data.get("id")
            room_id = data.get("roomId")
            user_id = data.get("personId")
            text = data.get("text")
            return {
                "type": "message",
                "message_id": message_id,
                "room_id": room_id,
                "user_id": user_id,
                "text": text
            }

        return {"error": "Unknown event"}

    def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the full message details by message_id."""
        try:
            message = self.api.messages.get(message_id)
            return message
        except Exception as e:
            print(f"Error fetching message: {e}")
            return None

    def create_webhook(self, target_url: str, room_id: Optional[str] = None, resource: str = "messages", event: str = "created") -> Dict[str, Any]:
        """Create a webhook for monitoring messages or actions in a room."""
        webhook = self.api.webhooks.create(
            name="Webhook for Message or Action",
            targetUrl=target_url,
            resource=resource,
            event=event,
            roomId=room_id
        )
        return {"webhook_id": webhook.id, "name": webhook.name, "resource": webhook.resource, "event": webhook.event}

    def get_webhooks(self) -> list:
        """Retrieve all webhooks."""
        webhooks = self.api.webhooks.list()
        return [{"webhook_id": webhook.id, "name": webhook.name} for webhook in webhooks]

    def delete_webhook(self, webhook_id: str) -> Dict[str, str]:
        """Delete a webhook by webhook_id."""
        self.api.webhooks.delete(webhook_id)
        return {"status": "deleted", "webhook_id": webhook_id}