# encryption/encryptor.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class Encryptor:
    def __init__(self, password: str):
        self.key = self._generate_key(password)
        self.fernet = Fernet(self.key)

    def _generate_key(self, password: str) -> bytes:
        salt = b'secure_cloud_salt'  # In production, use a random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def encrypt(self, data: bytes) -> bytes:
        return self.fernet.encrypt(data)

    def decrypt(self, encrypted_data: bytes) -> bytes:
        return self.fernet.decrypt(encrypted_data)