import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    FRAGMENT_SIZE = 1024 * 1024  # 1MB
    ENCRYPTED_FOLDER_NAME = 'SecureCloudStorage'

    # Cloud Service Credentials
    GOOGLE_CREDENTIALS = os.getenv('GOOGLE_CREDENTIALS')
    ONEDRIVE_CLIENT_ID = os.getenv('ONEDRIVE_CLIENT_ID')
    ONEDRIVE_CLIENT_SECRET = os.getenv('ONEDRIVE_CLIENT_SECRET')
    BOX_CLIENT_ID = os.getenv('BOX_CLIENT_ID')
    BOX_CLIENT_SECRET = os.getenv('BOX_CLIENT_SECRET')