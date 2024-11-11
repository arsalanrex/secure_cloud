# run_localdrive.py
from flask import Flask, request, send_file, jsonify
from cloud_services.localdrive_service import LocalDriveService
from pathlib import Path
import mimetypes
import os

app = Flask(__name__)
drive_service = LocalDriveService()


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
    try:
        data = drive_service.download_fragment(file_path)
        mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        return send_file(
            io.BytesIO(data),
            mimetype=mime_type,
            as_attachment=True,
            download_name=os.path.basename(file_path)
        )
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404


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


if __name__ == '__main__':
    app.run(port=5001, debug=True)