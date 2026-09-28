import requests
from requests.auth import HTTPBasicAuth
from app.config import (
    REDFISH_HOST,
    REDFISH_USERNAME,
    REDFISH_PASSWORD,
    REDFISH_VERIFY_SSL,
    REDFISH_SCHEME,
)


class RedfishClient:
    def __init__(self):
        self.base_url = f"{REDFISH_SCHEME}://{REDFISH_HOST}/redfish/v1"
        self.auth = HTTPBasicAuth(REDFISH_USERNAME, REDFISH_PASSWORD)

    def get(self, endpoint: str = ""):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.get(
            url,
            auth=self.auth,
            verify=REDFISH_VERIFY_SSL,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def get_root(self):
        return self.get()

    def get_systems(self):
        return self.get("Systems")

    def get_chassis(self):
        return self.get("Chassis")

    def get_managers(self):
        return self.get("Managers")