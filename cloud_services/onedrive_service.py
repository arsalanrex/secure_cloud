#cloud_services/onedrive_service.py
from typing import List, Dict
import onedrivesdk
from onedrivesdk.helpers import GetAuthCodeServer
from .base_cloud import BaseCloudService
from config import Config
import io


class OneDriveService(BaseCloudService):
    def __init__(self):
        self.client = None
        self.folder_id = None
        self.redirect_uri = "http://localhost:8080/"
        self.scopes = ['wl.signin', 'wl.offline_access', 'onedrive.readwrite']

    def authenticate(self) -> bool:
        http_provider = onedrivesdk.HttpProvider()
        auth_provider = onedrivesdk.AuthProvider(
            http_provider=http_provider,
            client_id=Config.ONEDRIVE_CLIENT_ID,
            scopes=self.scopes
        )

        client = onedrivesdk.OneDriveClient(
            Config.ONEDRIVE_BASE_URL,
            auth_provider,
            http_provider
        )

        auth_url = client.auth_provider.get_auth_url(self.redirect_uri)
        code = GetAuthCodeServer.get_auth_code(auth_url, self.redirect_uri)
        client.auth_provider.authenticate(code, self.redirect_uri, Config.ONEDRIVE_CLIENT_SECRET)

        self.client = client
        return True

    def create_secure_folder(self) -> str:
        if not self.folder_id:
            f = onedrivesdk.Folder()
            i = onedrivesdk.Item()
            i.name = Config.ENCRYPTED_FOLDER_NAME
            i.folder = f

            folder = self.client.item(drive='me', id='root').children.add(i)
            self.folder_id = folder.id

        return self.folder_id

    def upload_fragment(self, fragment_data: bytes, fragment_name: str) -> str:
        fragment_stream = io.BytesIO(fragment_data)
        uploaded_item = self.client.item(drive='me', id=self.folder_id) \
            .children[fragment_name] \
            .upload(fragment_stream)
        return uploaded_item.id

    def download_fragment(self, fragment_id: str) -> bytes:
        fragment_item = self.client.item(drive='me', id=fragment_id)
        fragment_stream = fragment_item.download()
        return fragment_stream.read()

    def list_fragments(self) -> List[Dict]:
        items = self.client.item(drive='me', id=self.folder_id).children.get()
        return [{
            'id': item.id,
            'name': item.name,
            'size': item.size
        } for item in items]