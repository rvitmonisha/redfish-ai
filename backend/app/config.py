import os
from dotenv import load_dotenv

load_dotenv()

REDFISH_HOST = os.getenv("REDFISH_HOST", "127.0.0.1:5000")
REDFISH_USERNAME = os.getenv("REDFISH_USERNAME", "")
REDFISH_PASSWORD = os.getenv("REDFISH_PASSWORD", "")
REDFISH_VERIFY_SSL = os.getenv("REDFISH_VERIFY_SSL", "false").lower() == "true"
REDFISH_SCHEME = os.getenv("REDFISH_SCHEME", "http")