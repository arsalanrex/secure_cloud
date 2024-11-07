#cloud_service/box_service.py
from typing import List, Dict
from boxsdk import OAuth2, Client
from boxsdk.exception import BoxAPIException
from .base_cloud import BaseCloudService
from config import Config
import io


class BoxService(BaseCloudService):
    def __init__(self):
        self.client = None
        self.folder_id = None

    def authenticate(self) -> bool:
        auth = OAuth2(
            client_id=Config.BOX_CLIENT_ID,
            client_secret=Config.BOX_CLIENT_SECRET,
            store_tokens=self._store_tokens
        )

        self.client = Client(auth)
        try:
            user = self.client.user().get()
            return True
        except BoxAPIException:
            return False

    def _store_tokens(self, access_token, refresh_token):
        # In production, store these securely
        # For demo purposes, we'll just keep them in memory
        self._access_token = access_token
        self._refresh_token = refresh_token

    def create_secure_folder(self) -> str:
        if not self.folder_id:
            try:
                folder = self.client.folder('0').create_subfolder(Config.ENCRYPTED_FOLDER_NAME)
                self.folder_id = folder.id
            except BoxAPIException as e:
                if 'folder already exists' in str(e):
                    # Find existing folder
                    items = self.client.folder('0').get_items()
                    for item in items:
                        if item.name == Config.ENCRYPTED_FOLDER_NAME:
                            self.folder_id = item.id
                            break
                else:
                    raise

        return self.folder_id

    def upload_fragment(self, fragment_data: bytes, fragment_name: str) -> str:
        fragment_stream = io.BytesIO(fragment_data)
        uploaded_file = self.client.folder(self.folder_id) \
            .upload_stream(fragment_stream, fragment_name)
        return uploaded_file.id

    def download_fragment(self, fragment_id: str) -> bytes:
        fragment_file = self.client.file(fragment_id).get()
        fragment_content = fragment_file.content()
        return fragment_content

    def list_fragments(self) -> List[Dict]:
        items = self.client.folder(self.folder_id).get_items()
        return [{
            'id': item.id,
            'name': item.name,
            'size': item.size
        } for item in items]

    def delete_fragment(self, fragment_id: str) -> bool:
        try:
            self.client.file(fragment_id).delete()
            return True
        except BoxAPIException as e:
            print(f"Error deleting fragment from Box: {str(e)}")
            return False
