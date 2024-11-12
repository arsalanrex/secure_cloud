# utils/metadata_manager.py
import json
import os
from typing import Dict, List, Optional
import os
import mimetypes
from datetime import datetime

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

    def format_file_size(self, size_in_bytes: int) -> str:
        """Format file size in KB, MB, or GB."""
        size_in_kb = size_in_bytes / 1024
        size_in_mb = size_in_kb / 1024
        size_in_gb = size_in_mb / 1024

        if size_in_gb >= 1:
            return f"{size_in_gb:.2f} GB"
        elif size_in_mb >= 1:
            return f"{size_in_mb:.2f} MB"
        else:
            return f"{size_in_kb:.2f} KB"

    def list_all_files(self) -> List[Dict]:
        """List metadata for all files."""
        files = []
        try:
            # Ensure the directory exists
            if not os.path.exists(self.storage_path):
                raise FileNotFoundError(f"Directory {self.storage_path} does not exist.")

            # Iterate over the files in the directory
            for filename in os.listdir(self.storage_path):
                if filename.endswith('.json'):  # Process only .json files
                    print(f"Found file: {filename}")  # Console output for debugging
                    file_id = filename[:-5]  # Remove '.json' extension
                    metadata = self.get_file_metadata(file_id)
                    if metadata:
                        # Adding additional metadata like size, mime_type, modified
                        file_path = os.path.join(self.storage_path, filename)

                        # Get the size in bytes and format it
                        size_in_bytes = metadata['total_size']
                        formatted_size = self.format_file_size(size_in_bytes)

                        # Get MIME type based on the file extension
                        mime_type, _ = mimetypes.guess_type(metadata['filename'])
                        mime_type = mime_type or 'unknown'  # Fallback if MIME type is not found

                        # Get the last modified time
                        modified_time = os.path.getmtime(file_path)
                        modified_str = datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d %H:%M:%S')

                        # Update metadata with the new fields
                        metadata['size'] = formatted_size
                        metadata['mime_type'] = mime_type
                        metadata['modified'] = modified_str
                        print(f"metadata Found file: {metadata}")
                        files.append(metadata)
        except Exception as e:
            print(f"An error occurred: {e}")

        return files