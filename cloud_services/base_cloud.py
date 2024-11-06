#cloud_services/base_cloud.py
from abc import ABC, abstractmethod
from typing import List, Dict


class BaseCloudService(ABC):
    """Abstract base class for cloud service implementations."""

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the cloud service."""
        pass

    @abstractmethod
    def create_secure_folder(self) -> str:
        """Create the encrypted folder if it doesn't exist."""
        pass

    @abstractmethod
    def upload_fragment(self, fragment_data: bytes, fragment_name: str) -> str:
        """Upload an encrypted fragment to the cloud."""
        pass

    @abstractmethod
    def download_fragment(self, fragment_id: str) -> bytes:
        """Download an encrypted fragment from the cloud."""
        pass

    @abstractmethod
    def list_fragments(self) -> List[Dict]:
        """List all fragments in the secure folder."""
        pass
