import os
import requests
from msal import ConfidentialClientApplication
from config import Config


class OneDriveService:
    def __init__(self):
        self.client_id = Config.ONEDRIVE_CLIENT_ID
        self.client_secret = Config.ONEDRIVE_CLIENT_SECRET
        self.tenant_id = 'your-tenant-id'  # Update this to your Azure AD tenant ID
        self.scope = ['https://graph.microsoft.com/.default']
        self.access_token = None
        self.authenticate()

    def authenticate(self):
        app = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}"
        )

        result = app.acquire_token_for_client(scopes=self.scope)
        if "access_token" in result:
            self.access_token = result['access_token']
        else:
            raise Exception("Could not obtain access token")

    def create_secure_folder(self, folder_name):
        """Creates a folder in the OneDrive root directory."""
        url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        folder_data = {
            "name": folder_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename"
        }
        response = requests.post(url, json=folder_data, headers=headers)
        response.raise_for_status()
        return response.json()['id']

    def upload_fragment(self, fragment_data, fragment_name, folder_id):
        """Uploads a file fragment to the specified folder."""
        url = f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}:/{fragment_name}:/content"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/octet-stream"
        }
        response = requests.put(url, data=fragment_data, headers=headers)
        response.raise_for_status()
        return response.json()['id']

    def list_fragments(self, folder_id):
        """Lists all fragments in the specified folder."""
        url = f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}/children"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        fragments = response.json().get('value', [])
        return [
            {'id': fragment['id'], 'name': fragment['name'], 'size': fragment['size']}
            for fragment in fragments
        ]

    def download_fragment(self, fragment_id):
        """Downloads a specific fragment by ID."""
        url = f"https://graph.microsoft.com/v1.0/me/drive/items/{fragment_id}/content"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()

        # Returning raw content; adjust as needed to handle content in the application
        return response.content

    def delete_fragment(self, fragment_id):
        """Deletes a specific fragment by ID."""
        url = f"https://graph.microsoft.com/v1.0/me/drive/items/{fragment_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.delete(url, headers=headers)
        response.raise_for_status()

        return response.status_code == 204
