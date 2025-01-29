# test_installation.py
from post import Webex, Outlook

# webex = Webex(client_id="your_client_id", client_secret="your_client_secret")
# webex.send_message("Hello, Webex!")

outlook = Outlook()
message_id = outlook.send_message(body="Hello, Outlook!", subject="Test Email", to_email="rishabravikumar@yahoo.com")
print(message_id)