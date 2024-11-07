# utils/metadata_manager.py
import json
import os
from typing import Dict, List, Optional

class MetadataManager:
    def __init__(self, storage_path: str = "metadata"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    def save_file_metadata(self, file_id: str, metadata: Dict) -> None:
        """Save metadata for a file."""
        metadata_path = os.path.join(self.storage_path, f"{file_id}.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)

    def get_file_metadata(self, file_id: str) -> Optional[Dict]:
        """Retrieve metadata for a file."""
        metadata_path = os.path.join(self.storage_path, f"{file_id}.json")
        try:
            with open(metadata_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def delete_file_metadata(self, file_id: str) -> bool:
        """Delete metadata for a file."""
        metadata_path = os.path.join(self.storage_path, f"{file_id}.json")
        try:
            os.remove(metadata_path)
            return True
        except FileNotFoundError:
            return False

    def list_all_files(self) -> List[Dict]:
        """List metadata for all files."""
        files = []
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                file_id = filename[:-5]  # Remove .json extension
                metadata = self.get_file_metadata(file_id)
                if metadata:
                    files.append(metadata)
        return files