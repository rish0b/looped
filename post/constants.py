# General messages
ERROR_MISSING_CREDENTIALS = "Missing required credentials."
ERROR_AUTHENTICATION_FAILED = "Failed to authenticate with {platform}."
ERROR_MESSAGE_SEND_FAILED = "Failed to send {type} on {platform}."

# Polling messages
POLLING_TIMEOUT = "Polling timed out for message ID {message_id}."
POLLING_SUCCESS = "Polling succeeded for message ID {message_id}."

### INTEGRATIONS ###

# Webex API Endpoints
WEBEX_BASE_URL = "https://webexapis.com/v1"
WEBEX_MESSAGES_ENDPOINT = f"{WEBEX_BASE_URL}/messages"
WEBEX_ATTACHMENT_ACTIONS_ENDPOINT = f"{WEBEX_BASE_URL}/attachment/actions"
WEBEX_WEBHOOKS_ENDPOINT = f"{WEBEX_BASE_URL}/webhooks"

# Outlook API Endpoints
OUTLOOK_BASE_URL = "https://graph.microsoft.com/v1.0"
OUTLOOK_SEND_MAIL_ENDPOINT = f"{OUTLOOK_BASE_URL}/me/sendMail"
OUTLOOK_MESSAGES_ENDPOINT = f"{OUTLOOK_BASE_URL}/me/messages"
OUTLOOK_SUBSCRIPTIONS_ENDPOINT = f"{OUTLOOK_BASE_URL}/subscriptions"
# tenant id can be set to "common" for most cases. allow users to pass in tenant_id if they belong to an org
OUTLOOK_TOKEN_URL = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
OUTLOOK_SCOPE_URL = "https://graph.microsoft.com/.default"