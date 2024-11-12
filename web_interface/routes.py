from flask import Blueprint, render_template, request, redirect, url_for, session, send_file
from werkzeug.utils import secure_filename
import mimetypes
from datetime import datetime
import os

from cloud_services.localdrive_service import LocalDriveService
from encryption.encryptor import Encryptor
from encryption.fragmenter import Fragmenter
from utils.metadata_manager import MetadataManager
from cloud_services.gdrive_service import GoogleDriveService
from cloud_services.onedrive_service import OneDriveService
from cloud_services.box_service import BoxService
from config import Config
import uuid
import io

main_bp = Blueprint('main', __name__)
metadata_manager = MetadataManager()


def get_cloud_service(service_name):
    if service_name == 'gdrive':
        return GoogleDriveService(Config.GOOGLE_CREDENTIALS)
    elif service_name == 'onedrive':
        return OneDriveService()
    elif service_name == 'box':
        return BoxService()
    elif service_name == 'local':  # Add this
        return LocalDriveService()
    raise ValueError(f"Unknown cloud service: {service_name}")


@main_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    return redirect(url_for('main.dashboard'))


@main_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    files = metadata_manager.list_all_files()
    return render_template('dashboard.html', files=files)


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cloud_service = request.form.get('cloud_service')
        encryption_key = request.form.get('encryption_key')

        try:
            service = get_cloud_service(cloud_service)
            if service.authenticate():
                session['cloud_service'] = cloud_service
                session['encryption_key'] = encryption_key
                session['user_id'] = str(uuid.uuid4())
                service.create_secure_folder()
                return redirect(url_for('main.dashboard'))
        except Exception as e:
            return render_template('login.html', error=str(e))

    return render_template('login.html')


@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))


@main_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('main.dashboard'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('main.dashboard'))

    if file:
        filename = secure_filename(file.filename)
        file_data = file.read()
        file_id = str(uuid.uuid4())

        encryptor = Encryptor(session['encryption_key'])
        fragmenter = Fragmenter()

        encrypted_data = encryptor.encrypt(file_data)
        fragments = fragmenter.fragment_file(encrypted_data)

        cloud_service = get_cloud_service(session['cloud_service'])
        fragment_ids = []

        for i, fragment in enumerate(fragments):
            fragment_name = f"{file_id}_fragment_{i}"
            fragment_id = cloud_service.upload_fragment(fragment, fragment_name)
            fragment_ids.append(fragment_id)

        metadata = {
            'id': file_id,
            'filename': filename,
            'fragments': fragment_ids,
            'total_size': len(file_data),
            'cloud_service': session['cloud_service']
        }
        metadata_manager.save_file_metadata(file_id, metadata)

        return redirect(url_for('main.dashboard'))



@main_bp.route('/download/<file_id>')
def download_file(file_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    metadata = metadata_manager.get_file_metadata(file_id)
    if not metadata:
        return "File not found", 404

    cloud_service = get_cloud_service(metadata['cloud_service'])
    fragments = []

    for fragment_id in metadata['fragments']:
        fragment_data = cloud_service.download_fragment(fragment_id)
        fragments.append(fragment_data)

    fragmenter = Fragmenter()
    encryptor = Encryptor(session['encryption_key'])

    encrypted_data = fragmenter.reconstruct_file(fragments)
    file_data = encryptor.decrypt(encrypted_data)

    return send_file(
        io.BytesIO(file_data),
        download_name=metadata['filename'],
        as_attachment=True
    )


@main_bp.route('/delete/<file_id>', methods=['POST'])
def delete_file(file_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    metadata = metadata_manager.get_file_metadata(file_id)
    if metadata:
        cloud_service = get_cloud_service(metadata['cloud_service'])
        for fragment_id in metadata['fragments']:
            try:
                cloud_service.delete_fragment(fragment_id)
            except:
                pass
        metadata_manager.delete_file_metadata(file_id)

    return redirect(url_for('main.dashboard'))