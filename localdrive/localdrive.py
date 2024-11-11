# localdrive/localdrive.py


from flask import Flask, request, send_file, jsonify, render_template
from cloud_services.localdrive_service import LocalDriveService
from config import LocalDriveConfig
from pathlib import Path
import mimetypes
import os
from dotenv import load_dotenv

# Load environment variables from the main .env file
main_env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=main_env_path)

# Calculate the correct template folder path
template_dir = Path(__file__).parent.parent / 'web_interface' / 'templates'

# Initialize Flask app with correct template directory
app = Flask(__name__, template_folder=str(template_dir))
app.config.from_object(LocalDriveConfig)

drive_service = LocalDriveService()

# Define path to SecureCloudStorage directory
SECURE_STORAGE_PATH = Path(__file__).parent / 'data' / 'SecureCloudStorage'

# Rest of your routes remain the same...
@app.route('/')
def list_files():
    # List files in SecureCloudStorage directory
    if SECURE_STORAGE_PATH.exists():
        files = [str(file.relative_to(SECURE_STORAGE_PATH)) for file in SECURE_STORAGE_PATH.glob('*') if file.is_file()]
    else:
        files = []

    return render_template('localdrive.html', files=files)


@app.route('/api/folders', methods=['POST'])
def create_folder():
    path = request.json.get('path')
    if not path:
        return jsonify({'error': 'Path is required'}), 400

    result = drive_service.create_folder(path)
    return jsonify(result)


@app.route('/api/files/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    path = request.form.get('path', '')

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    result = drive_service.upload_fragment(file.read(), str(Path(path) / file.filename))
    return jsonify({'id': result})


@app.route('/api/files/download/<path:file_path>')
def download_file(file_path):
    # Define the full file path
    full_path = SECURE_STORAGE_PATH / file_path
    if not full_path.is_file():
        return jsonify({'error': 'File not found'}), 404

    mime_type = mimetypes.guess_type(str(full_path))[0] or 'application/octet-stream'
    return send_file(
        full_path,
        mimetype=mime_type,
        as_attachment=True,
        download_name=full_path.name
    )


@app.route('/api/files/move', methods=['POST'])
def move_item():
    source = request.json.get('source')
    destination = request.json.get('destination')

    if not source or not destination:
        return jsonify({'error': 'Source and destination are required'}), 400

    success = drive_service.move_item(source, destination)
    return jsonify({'success': success})


@app.route('/api/files/copy', methods=['POST'])
def copy_item():
    source = request.json.get('source')
    destination = request.json.get('destination')

    if not source or not destination:
        return jsonify({'error': 'Source and destination are required'}), 400

    success = drive_service.copy_item(source, destination)
    return jsonify({'success': success})


@app.route('/api/files/preview/<path:file_path>')
def get_preview(file_path):
    preview_path = drive_service.get_file_preview(file_path)
    if preview_path:
        return send_file(preview_path)
    return jsonify({'error': 'Preview not available'}), 404


@app.route('/api/stats')
def get_stats():
    return jsonify(drive_service.get_stats())