# config.py
import os
import secrets
from dotenv import load_dotenv


def get_or_create_secret_key():
    env_path = '.env'

    # Load existing .env file
    load_dotenv(env_path)

    # Check if SECRET_KEY exists in .env
    secret_key = os.getenv('SECRET_KEY')

    if not secret_key or secret_key == 'your-secret-key-here' or secret_key == 'your-generated-secret-key-here':
        # Generate new secret key
        secret_key = secrets.token_hex(32)

        # Read existing .env content
        env_content = []
        if os.path.exists(env_path):
            with open(env_path, 'r') as file:
                env_content = file.readlines()

        # Update or add SECRET_KEY
        secret_key_line = f"SECRET_KEY={secret_key}\n"
        secret_key_found = False

        for i, line in enumerate(env_content):
            if line.startswith('SECRET_KEY='):
                env_content[i] = secret_key_line
                secret_key_found = True
                break

        if not secret_key_found:
            env_content.append(secret_key_line)

        # Write back to .env
        with open(env_path, 'w') as file:
            file.writelines(env_content)

    return secret_key


class Config:
    SECRET_KEY = get_or_create_secret_key()
    FRAGMENT_SIZE = 1024 * 1024  # 1MB
    ENCRYPTED_FOLDER_NAME = 'SecureCloudStorage'

    # Cloud Service Credentials
    GOOGLE_CREDENTIALS = os.getenv('GOOGLE_CREDENTIALS')
    ONEDRIVE_CLIENT_ID = os.getenv('ONEDRIVE_CLIENT_ID')
    ONEDRIVE_CLIENT_SECRET = os.getenv('ONEDRIVE_CLIENT_SECRET')
    BOX_CLIENT_ID = os.getenv('BOX_CLIENT_ID')
    BOX_CLIENT_SECRET = os.getenv('BOX_CLIENT_SECRET')