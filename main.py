import time
from post import Webex

# Initialize the Webex client with your access token
webex = Webex()

room_id = "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vYjMyYWQxOTAtZGU4MS0xMWVmLTg4MDItOWRiNmU1MDk4NmM3"

# Test sending a text message to a room and direct message to a user (by email)
def test_send_message():
    text_message = "Hello, Webex! Testing message to a room."
    email = "rishabravikumar@gmail.com"  # Test email address (send to Webex linked with this email)

    # Send to room
    send_room_msg = webex.send_message(room_id, text_message)
    print(f"Message sent to room: {send_room_msg}")

    # Send to email
    send_email_msg = webex.send_message(room_id, text_message, to_person_email=email)
    print(f"Message sent to email: {send_email_msg}")

    return send_email_msg

# Test sending an adaptive card
def test_send_card():
    card = {
        "type": "AdaptiveCard",
        "version": "1.0",
        "body": [
            {
                "type": "TextBlock",
                "text": "This is an Adaptive Card sent via Webex",
                "size": "Medium"
            }
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Submit",
                "id": "submit-action"
            }
        ]
    }

    # Send the card to room
    send_card_response = webex.send_card(room_id, card)
    print(f"Adaptive card sent: {send_card_response}")

# Test handling webhook event (simulate incoming data)
def test_handle_webhook_event():
    webhook_data_message = {
        "resource": "messages",
        "event": "created",
        "data": {
            "id": "message-id",
            "roomId": "room-id",
            "personId": "user-id",
            "text": "This is a test message"
        }
    }

    webhook_data_card = {
        "resource": "messages",
        "event": "attachmentAction",
        "data": {
            "data": {
                "messageId": "message-id",
                "roomId": "room-id",
                "actorId": "user-id",
                "inputs": {"action": "submitted"},
                "id": "action-id"
            }
        }
    }

    # Handle message event
    print("Handling message event...")
    message_response = webex.handle_webhook_event(webhook_data_message)
    print(f"Message event response: {message_response}")

    # Handle card response event
    print("Handling card response event...")
    card_response = webex.handle_webhook_event(webhook_data_card)
    print(f"Card response event: {card_response}")

# Test retrieving a message by message_id
def test_get_message(message_id:str):
    message_id = message_id # Replace with a valid message ID
    message_details = webex.get_message(message_id)
    print(f"Message details: {message_details}")

# Test creating, retrieving, and deleting a webhook
def test_webhook():
    webhook_url = "YOUR_WEBHOOK_URL"  # Replace with your webhook URL

    # Create a webhook
    webhook_response = webex.create_webhook(target_url=webhook_url, room_id=room_id)
    print(f"Webhook created: {webhook_response}")

    # Get webhooks
    webhooks = webex.get_webhooks()
    print(f"Current webhooks: {webhooks}")

    # Delete the webhook
    webhook_id = webhook_response["webhook_id"]
    delete_response = webex.delete_webhook(webhook_id)
    print(f"Webhook deleted: {delete_response}")

if __name__ == "__main__":
    # Run tests
    messageDict = test_send_message()
    print(messageDict)
    time.sleep(2)
    test_send_card()
    time.sleep(2)
    #test_handle_webhook_event()
    time.sleep(2)
    test_get_message(messageDict['message_id'])
    time.sleep(2)
    #test_webhook()