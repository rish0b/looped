import requests, aiohttp
from .auth_manager import AuthManager
from .handler import Handler
from .utils import setup_logger
from .config import WEBEX_ACCESS_TOKEN
from .constants import WEBEX_BASE_URL, WEBEX_MESSAGES_ENDPOINT, WEBEX_WEBHOOKS_ENDPOINT, WEBEX_DIRECT_MESSAGES_ENDPOINT

class Webex(AuthManager, Handler):
    
    def __init__(self, access_token=WEBEX_ACCESS_TOKEN, silent=False):
        super().__init__()
        self.logger = setup_logger(silent)
        self.access_token = access_token

    def authenticate(self):
        return super().authenticate()    
    
    def _construct_filter(self, filter_room_id=None, filter_to_person_email=None, filter_mentioned_people=None, filter_action_ids=None):
        """
        Constructs the filter string based on the given parameters, including multiple actionIds for attachment actions.
        """
        filters = []
        
        if filter_room_id:
            filters.append(f"roomId={filter_room_id}")
        if filter_to_person_email:
            filters.append(f"toPersonEmail={filter_to_person_email}")
        if filter_mentioned_people:
            filters.append(f"mentionedPeople={filter_mentioned_people}")
        if filter_action_ids:
            action_ids_str = ",".join(filter_action_ids) if isinstance(filter_action_ids, list) else filter_action_ids
            filters.append(f"actionId={action_ids_str}")  # Handle multiple actionIds as a comma-separated string
        
        return " AND ".join(filters) if filters else None

    def register_webhook(self, name, target_url, resource="messages", event="created", filter_room_id=None, filter_to_person_email=None, filter_mentioned_people=None, filter_action_ids=None):
        """
        Registers a new Webex webhook with filters constructed automatically, now including multiple actionIds for attachment actions.
        
        - name: Webhook name (used for identification)
        - target_url: Callback URL that will receive the event data
        - resource: Type of resource to listen to (e.g., messages, memberships, attachment-actions)
        - event: Event that triggers the webhook (e.g., created, updated, deleted)
        - filter_room_id: Optional roomId filter
        - filter_to_person_email: Optional toPersonEmail filter
        - filter_mentioned_people: Optional mentionedPeople filter
        - filter_action_ids: Optional list of actionIds to filter attachment actions
        :return: Webhook ID
        """
        headers = {"Authorization": f"Bearer {self.access_token}"}
        filter_str = self._construct_filter(filter_room_id=filter_room_id, filter_to_person_email=filter_to_person_email, filter_mentioned_people=filter_mentioned_people, filter_action_ids=filter_action_ids)
        
        data = {
            "name": name,             # Webhook identifier
            "targetUrl": target_url,  # Callback URL
            "resource": resource,     # What resource to listen to (e.g., "messages", "attachment-actions")
            "event": event,           # Event type to listen to (e.g., "created")
        }

        if filter_str:
            data["filter"] = filter_str  # Automatically constructed filter string

        # Register the webhook
        try:
            response = requests.post(WEBEX_WEBHOOKS_ENDPOINT, json=data, headers=headers)
            response.raise_for_status()
            webhook_id = response.json().get("id")
            self.logger.info(f"Webhook registered with ID: {webhook_id}")
            return webhook_id
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error registering webhook: {e}")
            return None
    
    def send_message(self, body, to_email=None, to_room_id=None, attachments=None, adaptive_card=None, include_full_response=False, parent_id=None, to_person_id=None, markdown=None):
        """
        Sends a message to Webex, with support for different message types, including rich formatting and attachments.

        Parameters:
        - body (str): The main body of the message (required).
        - to_email (str, optional): The email address of the recipient for sending to a specific person.
        - to_room_id (str, optional): The ID of the Webex room to send the message to.
        - attachments (list, optional): A list of attachments (e.g., files) to send along with the message.
        - card_content (dict, optional): The content of an Adaptive Card to send (in JSON format).
        - include_full_response (bool, optional): If True, returns the full Webex response; otherwise, only message ID and room ID.
        - parent_id (str, optional): The ID of the message to reply to (for threaded conversations).
        - to_person_id (str, optional): The ID of the person to send a private 1:1 message to.
        - markdown (str, optional): The message body in Markdown format for richer formatting (e.g., bold, italics, lists).

        Returns:
        - tuple: If include_full_response is False, returns a tuple containing the message ID, room ID, and the card content if an adaptive card was sent.
        - dict: If include_full_response is True, returns the full Webex response as a dictionary.
        """
        headers = {"Authorization": f"Bearer {self.access_token}"}
        data = {}

        # Determine the recipient based on provided parameters
        if to_room_id:
            data["roomId"] = to_room_id
        elif to_person_id:
            data["toPersonId"] = to_person_id
        elif to_email:
            data["toPersonEmail"] = to_email
        else:
            raise ValueError("Either to_room_id, to_person_id, or to_email must be provided.")

        # Set the message body (Markdown support or plain text)
        if markdown:
            data["markdown"] = markdown
        else:
            data["text"] = body

        # Set parent message for replies (if replying to an existing message)
        if parent_id:
            data["parentId"] = parent_id

        # Add attachments (including Adaptive Cards) if provided
        if attachments:
            data["attachments"] = attachments

        if adaptive_card:
            data["attachments"] = [{"contentType": "application/vnd.microsoft.card.adaptive", "content": adaptive_card}]

        # Send the request to Webex API
        response = requests.post(WEBEX_MESSAGES_ENDPOINT, json=data, headers=headers)

        # Handle potential errors from Webex API
        response.raise_for_status()

        # Process and return response based on the user's request
        response_json = response.json()

        # Return full response if requested
        if include_full_response:
            return response_json  # Return the full Webex response if requested

        # Extract the message ID and room ID for filtered response
        message_id = response_json.get("id")
        room_id = response_json.get("roomId")
        if adaptive_card:
            card_content = response_json.get("attachments", [{}])[0].get("content")
            return message_id, room_id, card_content  # Return card content if relevant

            # Return only basic details by default (for regular messages or with attachments)
        return message_id, room_id
    
    def check_for_feedback(self, room_id=None, parent_message_id=None, adaptive_card_only=False,
                        to_person_email=None, to_person_id=None, filter_max=50, filter_mentioned_people=None, 
                        filter_before=None, filter_before_message=None):
        """
        Checks for feedback messages in response to a specific message or Adaptive Card.
        
        Args:
            room_id (str, optional): The ID of the room to filter messages by (for group messages).
            parent_id (str, optional): The ID of the parent message to filter replies by.
            to_person_email (str, optional): The recipient’s email to check for direct messages.
            to_person_id (str, optional): The recipient’s person ID to check for direct messages.
            adaptive_card_only (bool, optional): If True, only messages with Adaptive Cards will be returned.
            filter_max (int, optional): The maximum number of messages to return (default 50).
            filter_mentioned_people (str, optional): If the bot should only look for messages mentioning specific people (default None).
            filter_before (str, optional): List messages sent before a specific date/time (ISO 8601 format).
            filter_before_message (str, optional): List messages sent before a specific message ID.
            
        Returns:
            list: A list of feedback messages, including any relevant Adaptive Card content.
        """
        headers = {"Authorization": f"Bearer {self.access_token}"}
        try:
            # Construct query parameters based on the provided filters
            params = {
                "max": filter_max,
                "parentId": parent_message_id,
                "mentionedPeople": filter_mentioned_people,
                "before": filter_before,
                "beforeMessage": filter_before_message,
            }

            # Decide which endpoint to use based on the presence of `to_person_email` or `to_person_id`
            if to_person_email or to_person_id:
                # For direct messages
                params["personEmail"] = to_person_email
                params["personId"] = to_person_id
                endpoint = WEBEX_DIRECT_MESSAGES_ENDPOINT
            else:
                # For group messages
                params["roomId"] = room_id
                endpoint = WEBEX_MESSAGES_ENDPOINT

            # Make the request to Webex
            response = requests.get(endpoint, params=params, headers=headers)
            response.raise_for_status()

            feedback_data = response.json()

            # If filtering for Adaptive Cards only, we need to post-process the data
            if adaptive_card_only:
                feedback_data = [
                    feedback for feedback in feedback_data["items"]
                    if any(attachment.get("contentType") == "application/vnd.microsoft.card.adaptive"
                        for attachment in feedback.get("attachments", []))
                ]

            # Collect feedback along with card content if present
            feedback_info = []
            for feedback in feedback_data.get("items", []):
                card_content = next(
                    (attachment.get("content") for attachment in feedback.get("attachments", [])
                    if attachment.get("contentType") == "application/vnd.microsoft.card.adaptive"), 
                    None
                )
                if card_content:
                    feedback["adaptive_card_content"] = card_content  # Attach Adaptive Card content

                feedback_info.append(feedback)

            return feedback_info
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching feedback: {e}")
            return []
        
    def retrieve_message(self, message_id):
        """
        Retrieves message details from Webex API using the provided message_id.
        
        :param message_id: The ID of the message you want to retrieve
        :return: The message details as a dictionary
        """
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"{WEBEX_MESSAGES_ENDPOINT}/{message_id}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()  # Return the message details as a JSON object
        else:
            # You can customize this to handle different status codes as needed
            print(f"Failed to retrieve message. Status code: {response.status_code}")
            return None  

    def list_webhooks(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(WEBEX_WEBHOOKS_ENDPOINT, headers=headers)
        response.raise_for_status()
        return response.json().get("items", [])

    def delete_webhook(self, webhook_id):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.delete(f"{WEBEX_WEBHOOKS_ENDPOINT}/{webhook_id}", headers=headers)
        response.raise_for_status()
        self.logger.info(f"Webhook {webhook_id} deleted.")
        return response.status_code == 204              