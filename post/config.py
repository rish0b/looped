from dotenv import load_dotenv, find_dotenv
import os

# Load the .env file if it exists
load_dotenv(find_dotenv())

# WEBEX
WEBEX_ACCESS_TOKEN = os.getenv("WEBEX_ACCESS_TOKEN")

# OUTLOOK
OUTLOOK_ACCESS_TOKEN = os.getenv("OUTLOOK_ACCESS_TOKEN")
OUTLOOK_TENANT_ID = os.getenv("OUTLOOK_TENANT_ID")
OUTLOOK_CLIENT_ID = os.getenv("OUTLOOK_CLIENT_ID")
OUTLOOK_CLIENT_SECRET = os.getenv("OUTLOOK_CLIENT_SECRET")