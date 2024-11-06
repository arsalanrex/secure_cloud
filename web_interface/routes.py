# web_interface/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    return render_template('dashboard.html')


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cloud_service = request.form.get('cloud_service')
        if cloud_service == 'gdrive':
            service = GoogleDriveService(Config.GOOGLE_CREDENTIALS)
        elif cloud_service == 'onedrive':
            # Initialize OneDrive service
            pass
        elif cloud_service == 'box':
            # Initialize Box service
            pass

        if service.authenticate():
            session['cloud_service'] = cloud_service
            session['user_id'] = True
            return redirect(url_for('main.dashboard'))

    return render_template('login.html')


@main_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if file:
        # Process file upload with encryption and fragmentation
        filename = secure_filename(file.filename)
        file_data = file.read()

        # Initialize services
        encryptor = Encryptor(session['encryption_key'])
        fragmenter = Fragmenter()

        # Encrypt and fragment file
        encrypted_data = encryptor.encrypt(file_data)
        fragments = fragmenter.fragment_file(encrypted_data)

        # Upload fragments to cloud
        cloud_service = get_cloud_service(session['cloud_service'])
        fragment_ids = []

        for i, fragment in enumerate(fragments):
            fragment_name = f"{filename}.fragment{i}"
            fragment_id = cloud_service.upload_fragment(fragment, fragment_name)
            fragment_ids.append(fragment_id)

        # Save metadata
        metadata = {
            'filename': filename,
            'fragments': fragment_ids,
            'total_size': len(file_data)
        }
        save_metadata(metadata)

        return redirect(url_for('main.dashboard'))