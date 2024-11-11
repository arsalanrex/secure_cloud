# cloud_services/localdrive_service.py
import os
import shutil
import json
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Union
from werkzeug.utils import secure_filename
from .base_cloud import BaseCloudService
from config import Config


class LocalDriveService(BaseCloudService):
    """Implementation of local drive storage service with cloud-like features."""

    def __init__(self, root_path: str = "localdrive"):
        """Initialize local drive service with root storage path."""
        self.root_path = Path(root_path)
        self.data_path = self.root_path / "data"
        self.meta_path = self.root_path / "metadata"
        self.temp_path = self.root_path / "temp"
        self._ensure_directories()

    def _ensure_directories(self):
        """Create necessary directory structure."""
        for path in [self.root_path, self.data_path, self.meta_path, self.temp_path]:
            path.mkdir(parents=True, exist_ok=True)

    def authenticate(self) -> bool:
        """Local authentication is always successful if directories exist."""
        return all(p.exists() for p in [self.root_path, self.data_path, self.meta_path])

    def create_secure_folder(self) -> str:
        """Create encrypted storage folder."""
        folder_path = self.data_path / Config.ENCRYPTED_FOLDER_NAME
        folder_path.mkdir(exist_ok=True)
        return str(folder_path)

    def _save_metadata(self, file_id: str, metadata: dict):
        """Save file metadata."""
        meta_file = self.meta_path / f"{file_id}.json"
        with open(meta_file, 'w') as f:
            json.dump(metadata, f)

    def _get_metadata(self, file_id: str) -> Optional[dict]:
        """Retrieve file metadata."""
        meta_file = self.meta_path / f"{file_id}.json"
        try:
            with open(meta_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def upload_fragment(self, fragment_data: bytes, fragment_name: str) -> str:
        """Upload a file fragment."""
        secure_name = secure_filename(fragment_name)
        file_path = self.data_path / Config.ENCRYPTED_FOLDER_NAME / secure_name

        with open(file_path, 'wb') as f:
            f.write(fragment_data)

        metadata = {
            'id': secure_name,
            'path': str(file_path),
            'size': len(fragment_data),
            'created_at': datetime.now().isoformat(),
            'mime_type': mimetypes.guess_type(secure_name)[0]
        }
        self._save_metadata(secure_name, metadata)

        return secure_name

    def download_fragment(self, fragment_id: str) -> bytes:
        """Download a file fragment."""
        metadata = self._get_metadata(fragment_id)
        if not metadata:
            raise FileNotFoundError(f"Fragment {fragment_id} not found")

        with open(metadata['path'], 'rb') as f:
            return f.read()

    def list_fragments(self) -> List[Dict]:
        """List all fragments in the secure folder."""
        fragments = []
        fragment_dir = self.data_path / Config.ENCRYPTED_FOLDER_NAME

        for file_path in fragment_dir.glob('*'):
            if file_path.is_file():
                metadata = self._get_metadata(file_path.name)
                if metadata:
                    fragments.append(metadata)

        return fragments

    def delete_fragment(self, fragment_id: str) -> bool:
        """Delete a fragment and its metadata."""
        metadata = self._get_metadata(fragment_id)
        if not metadata:
            return False

        try:
            # Delete the file
            os.remove(metadata['path'])
            # Delete metadata
            os.remove(self.meta_path / f"{fragment_id}.json")
            return True
        except OSError:
            return False

    # Additional cloud-like features
    def create_folder(self, path: str) -> Dict:
        """Create a new folder."""
        folder_path = self.data_path / path
        folder_path.mkdir(parents=True, exist_ok=True)

        metadata = {
            'id': str(folder_path.relative_to(self.data_path)),
            'name': folder_path.name,
            'path': str(folder_path),
            'type': 'folder',
            'created_at': datetime.now().isoformat()
        }
        self._save_metadata(metadata['id'], metadata)
        return metadata

    def move_item(self, source: str, destination: str) -> bool:
        """Move a file or folder to a new location."""
        src_path = self.data_path / source
        dst_path = self.data_path / destination

        try:
            shutil.move(str(src_path), str(dst_path))
            return True
        except OSError:
            return False

    def copy_item(self, source: str, destination: str) -> bool:
        """Copy a file or folder to a new location."""
        src_path = self.data_path / source
        dst_path = self.data_path / destination

        try:
            if src_path.is_file():
                shutil.copy2(str(src_path), str(dst_path))
            else:
                shutil.copytree(str(src_path), str(dst_path))
            return True
        except OSError:
            return False

    def get_file_preview(self, file_id: str, preview_size: tuple = (200, 200)) -> Optional[str]:
        """Generate preview for supported file types."""
        metadata = self._get_metadata(file_id)
        if not metadata:
            return None

        mime_type = metadata.get('mime_type', '')
        if mime_type.startswith('image/'):
            # For images, create thumbnail
            try:
                from PIL import Image
                img_path = metadata['path']
                preview_path = self.temp_path / f"preview_{file_id}"

                with Image.open(img_path) as img:
                    img.thumbnail(preview_size)
                    img.save(preview_path)

                return str(preview_path)
            except Exception:
                return None

        return None

    def get_stats(self) -> Dict:
        """Get storage statistics."""
        total_size = 0
        file_count = 0
        folder_count = 0

        for path in self.data_path.rglob('*'):
            if path.is_file():
                total_size += path.stat().st_size
                file_count += 1
            elif path.is_dir():
                folder_count += 1

        return {
            'total_size': total_size,
            'file_count': file_count,
            'folder_count': folder_count,
            'available_space': shutil.disk_usage(self.root_path).free
        }