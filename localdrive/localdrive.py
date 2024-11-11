# locadrive/localdrive.py

from flask import Flask, request, send_file, jsonify, render_template, abort
from cloud_services.localdrive_service import LocalDriveService
from config import LocalDriveConfig
from pathlib import Path
import mimetypes
import os
from dotenv import load_dotenv
from PIL import Image
import io
import fitz  # PyMuPDF for PDF preview
import tempfile
from werkzeug.utils import secure_filename

# Initialize mimetypes
mimetypes.init()

# Load environment variables from the main .env file
main_env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=main_env_path)

# Calculate the correct template folder path
template_dir = Path(__file__).parent.parent / 'web_interface' / 'templates'

# Initialize Flask app with correct template directory
app = Flask(__name__, template_folder=str(template_dir))
app.config.from_object(LocalDriveConfig)

drive_service = LocalDriveService()

# Define paths
SECURE_STORAGE_PATH = Path(__file__).parent / 'data' / 'SecureCloudStorage'
PREVIEW_CACHE_PATH = Path(__file__).parent / 'preview_cache'

# Ensure necessary directories exist
SECURE_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
PREVIEW_CACHE_PATH.mkdir(parents=True, exist_ok=True)

# Configure maximum preview sizes
MAX_PREVIEW_SIZE = (800, 800)  # Maximum preview dimensions for images
MAX_PREVIEW_FILE_SIZE = 50 * 1024 * 1024  # 50MB max file size for preview generation

def get_mime_type(file_path: Path) -> str:
    """Get MIME type of file using mimetypes library."""
    mime_type, _ = mimetypes.guess_type(str(file_path))
    return mime_type or 'application/octet-stream'

def get_file_info(file_path: Path):
    """Get detailed file information."""
    try:
        stats = file_path.stat()
        return {
            'name': file_path.name,
            'size': stats.st_size,
            'modified': stats.st_mtime,
            'mime_type': get_mime_type(file_path),
            'path': str(file_path.relative_to(SECURE_STORAGE_PATH))
        }
    except Exception as e:
        app.logger.error(f"Error getting file info: {e}")
        return None

def generate_image_preview(file_path: Path, preview_path: Path):
    """Generate image preview with maximum dimensions."""
    try:
        with Image.open(file_path) as img:
            img.thumbnail(MAX_PREVIEW_SIZE)
            img = img.convert('RGB')  # Convert to RGB to ensure JPEG compatibility
            img.save(preview_path, 'JPEG', quality=85)
        return True
    except Exception as e:
        app.logger.error(f"Error generating image preview: {e}")
        return False

def generate_pdf_preview(file_path: Path, preview_path: Path):
    """Generate preview for PDF files (first page only)."""
    try:
        doc = fitz.open(file_path)
        if doc.page_count > 0:
            page = doc[0]  # First page
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
            pix.save(preview_path)
        doc.close()
        return True
    except Exception as e:
        app.logger.error(f"Error generating PDF preview: {e}")
        return False

def get_preview_path(file_path: Path) -> Path:
    """Get or generate preview for a file."""
    if not file_path.exists() or file_path.stat().st_size > MAX_PREVIEW_FILE_SIZE:
        return None

    # Create preview filename based on original file's modification time
    preview_name = f"{file_path.stem}_{file_path.stat().st_mtime}.jpg"
    preview_path = PREVIEW_CACHE_PATH / preview_name

    # Return cached preview if it exists
    if preview_path.exists():
        return preview_path

    file_type = get_mime_type(file_path)

    # Generate preview based on file type
    success = False
    if file_type and file_type.startswith('image/'):
        success = generate_image_preview(file_path, preview_path)
    elif file_type == 'application/pdf':
        success = generate_pdf_preview(file_path, preview_path)

    return preview_path if success else None

@app.route('/')
def list_files():
    """List all files in the storage directory."""
    files = []
    if SECURE_STORAGE_PATH.exists():
        for file_path in SECURE_STORAGE_PATH.rglob('*'):
            if file_path.is_file():
                file_info = get_file_info(file_path)
                if file_info:
                    files.append(file_info)

    return render_template('localdrive.html', files=files)

@app.route('/api/files/upload', methods=['POST'])
def upload_file():
    """Handle file upload."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        filename = secure_filename(file.filename)
        file_path = SECURE_STORAGE_PATH / filename

        # Ensure unique filename
        counter = 1
        while file_path.exists():
            stem = file_path.stem.split('_')[0]  # Get original stem without counter
            file_path = SECURE_STORAGE_PATH / f"{stem}_{counter}{file_path.suffix}"
            counter += 1

        file.save(file_path)
        return jsonify({
            'success': True,
            'file': get_file_info(file_path)
        })

    except Exception as e:
        app.logger.error(f"Upload error: {e}")
        return jsonify({'error': 'Upload failed'}), 500

@app.route('/api/files/download/<path:file_path>')
def download_file(file_path):
    """Handle file download."""
    try:
        full_path = SECURE_STORAGE_PATH / file_path
        if not full_path.exists() or not full_path.is_file():
            return jsonify({'error': 'File not found'}), 404

        return send_file(
            full_path,
            as_attachment=True,
            download_name=full_path.name
        )
    except Exception as e:
        app.logger.error(f"Download error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/preview/<path:file_path>')
def get_preview(file_path):
    """Handle file preview."""
    try:
        full_path = SECURE_STORAGE_PATH / file_path
        if not full_path.exists() or not full_path.is_file():
            return jsonify({'error': 'File not found'}), 404

        preview_path = get_preview_path(full_path)
        if preview_path and preview_path.exists():
            return send_file(preview_path, mimetype='image/jpeg')

        # If no preview available, return the original file for supported types
        file_type = get_mime_type(full_path)

        if file_type and (file_type.startswith(('image/', 'text/')) or file_type == 'application/pdf'):
            return send_file(full_path)

        return jsonify({'error': 'Preview not available'}), 404

    except Exception as e:
        app.logger.error(f"Preview error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/delete/<path:file_path>', methods=['POST'])
def delete_file(file_path):
    """Handle file deletion."""
    try:
        full_path = SECURE_STORAGE_PATH / file_path
        if not full_path.exists() or not full_path.is_file():
            return jsonify({'error': 'File not found'}), 404

        # Delete associated preview if it exists
        preview_name = f"{full_path.stem}_{full_path.stat().st_mtime}.jpg"
        preview_path = PREVIEW_CACHE_PATH / preview_name
        if preview_path.exists():
            preview_path.unlink()

        # Delete the file
        full_path.unlink()
        return jsonify({'success': True})

    except Exception as e:
        app.logger.error(f"Delete error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get storage statistics."""
    try:
        total_files = 0
        total_size = 0
        file_types = {}

        for file_path in SECURE_STORAGE_PATH.rglob('*'):
            if file_path.is_file():
                total_files += 1
                size = file_path.stat().st_size
                total_size += size

                # Get file type
                file_type = get_mime_type(file_path)
                file_types[file_type] = file_types.get(file_type, 0) + 1

        return jsonify({
            'total_files': total_files,
            'total_size': total_size,
            'file_types': file_types
        })

    except Exception as e:
        app.logger.error(f"Stats error: {e}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500