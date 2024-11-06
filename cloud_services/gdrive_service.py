#cloud_services/gdrive_service.py
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from .base_cloud import BaseCloudService
import io


class GoogleDriveService(BaseCloudService):
    SCOPES = ['https://www.googleapis.com/auth/drive.file']

    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self.service = None
        self.folder_id = None

    def authenticate(self) -> bool:
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.service = build('drive', 'v3', credentials=creds)
        return True

    def create_secure_folder(self) -> str:
        if not self.folder_id:
            folder_metadata = {
                'name': Config.ENCRYPTED_FOLDER_NAME,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = self.service.files().create(
                body=folder_metadata, fields='id').execute()
            self.folder_id = folder.get('id')
        return self.folder_id

    def upload_fragment(self, fragment_data: bytes, fragment_name: str) -> str:
        file_metadata = {
            'name': fragment_name,
            'parents': [self.folder_id]
        }
        media = MediaIoBaseUpload(
            io.BytesIO(fragment_data),
            mimetype='application/octet-stream',
            resumable=True
        )
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        return file.get('id')