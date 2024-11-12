# Secure Cloud Storage

## Overview

Secure Cloud Storage is a cloud-based file storage application that ensures data security through encryption and fragmentation. This project addresses the need for secure data storage across multiple cloud platforms (Google Drive, OneDrive, and Box) as well as on a local drive. By dividing files into encrypted fragments and uploading these pieces separately, it enhances security and mitigates risks related to data breaches on cloud platforms.

This provides a solution to secure data storage and retrieval by leveraging multiple storage platforms. Encryption and fragmentation not only protect sensitive data but also distribute it across various locations, reducing vulnerability to unauthorized access.

## Features

- **Multiple Cloud Storage Support**: Integrates with Google Drive, OneDrive, Box, and local storage.
- **File Encryption**: Encrypts files before uploading them, using strong cryptographic algorithms.
- **File Fragmentation**: Splits encrypted files into fragments to enhance security.
- **File Reconstruction**: Reassembles file fragments and decrypts them locally upon download.
- **Web Interface**: Provides a user-friendly interface to upload, download, and manage files.


## Prerequisites

- Python 3.7+
- Flask web server
- Cloud service accounts (Google Drive, OneDrive, Box)
- Required Python packages (see requirements.txt)

## Technology Stack

- **Backend**: Python 3.9+
- **Web Framework**: Flask
- **Cloud Storage Integration**: Google Drive API, Microsoft Graph API (for OneDrive), Box SDK
- **Encryption**: Cryptography library (for file encryption using symmetric keys)
- **Fragmentation**: Custom Python logic for dividing files into fragments
- **Data Storage**:
  - **Cloud Storage**: Google Drive, OneDrive, Box
  - **Local Storage**: Local directory structure for local storage support
- **Frontend**: HTML, CSS, JavaScript (Tailwind CSS for styling)
- **Session Management**: Flask-Session
- **Environment Management**: python-dotenv
- **Testing**: Pytest
- **Image & PDF Processing**: Pillow (PIL) for image previews, PyMuPDF for PDF previews


## Installation

1. Clone the repository:
```bash
git clone https://github.com/arsalanrex/secure_cloud.git
cd secure_cloud

```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Create a `.env` file in the project root
   - Add the following configuration:
   - If SECRET_KEY is not provided, a random key will be generated and stored in .env
```env
# Google Drive
GOOGLE_CREDENTIALS=path/to/your/google-credentials.json

# OneDrive
ONEDRIVE_CLIENT_ID=your-onedrive-client-id
ONEDRIVE_CLIENT_SECRET=your-onedrive-client-secret

# Box
BOX_CLIENT_ID=your-box-client-id
BOX_CLIENT_SECRET=your-box-client-secret

# LocalDrive
encryption_key=your-encrytion-key

SECRET_KEY=your-generated-secret-key-here
```

## Cloud Service Setup

### Google Drive
1. Create a project in Google Cloud Console
2. Enable the Google Drive API
3. Create OAuth 2.0 credentials
4. Download the credentials JSON file
5. Set the path in `.env` as GOOGLE_CREDENTIALS

### OneDrive
1. Register your application in the Microsoft Azure Portal
2. Get the client ID and secret
3. Add them to `.env`

### Box
1. Create a Box developer account
2. Create a new Box application
3. Get the client ID and secret
4. Add them to `.env`


## Project Structure

```secure-cloud-storage
├── .env                          # Environment variables for cloud credentials
├── cloud_services                # Cloud storage services module
│   ├── __init__.py               # Module initializer
│   ├── base_cloud.py             # Abstract base class for cloud services
│   ├── box_service.py            # Box cloud storage service implementation
│   ├── gdrive_service.py         # Google Drive cloud storage service implementation
│   ├── localdrive_service.py     # Local storage service implementation
│   └── onedrive_service.py       # OneDrive cloud storage service implementation
├── config.py                     # Configuration file with encryption and fragment settings
├── encryption                    # Encryption and fragmentation module
│   ├── __init__.py               # Module initializer
│   ├── encryptor.py              # File encryption and decryption class
│   └── fragmenter.py             # File fragmentation and reassembly class
├── localdrive                    # Local storage directory
│   ├── data                      # SecureCloudStorage encrypted fragments storage
│   ├── localdrive.py             # Local storage file manager and preview generator
│   └── metadata                  # Metadata for uploaded files
├── metadata                      # Root-level metadata directory
├── requirements.txt              # Python dependencies list
├── run.py                        # Entry point for web server
├── run_localdrive.py             # Entry point for local drive server
├── utils                         # Utility scripts
│   ├── __init__.py               # Module initializer
│   └── metadata_manager.py       # Metadata manager
└── web_interface                 # Web interface for the application
    ├── app.py                    # Flask application setup
    ├── routes.py                 # Web routes for file management
    └── templates                 # HTML templates for web interface
```


## Usage

1. Start the application:

#### For Cloud Storage
```bash
python run.py
```
Access the client interface at `http://localhost:5000`

#### For Local Drive
```bash
python run_localdrive.py
```
Access the local drive interface at `http://localhost:5001`

2. Upload files:
   - Files are automatically encrypted
   - Split into fragments
   - Distributed across your cloud storage

3. Download files:
   - Files are automatically reassembled
   - Decrypted using your encryption key
   - Downloaded to your local machine

## Security Features

### Encryption
- Uses Fernet symmetric encryption
- Password-based key derivation using PBKDF2
- Secure salt handling

### File Fragmentation
- Files are split into manageable chunks
- Default fragment size: 1MB (configurable)
- Fragments are encrypted individually

### Metadata Management
- Secure storage of file metadata
- Tracks fragment distribution
- Manages reconstruction information

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The MIT License is a permissive license that is short and to the point. It lets people do almost anything they want with your project, like making and distributing closed source versions, as long as they include the original copyright and license notice.

## Contact

For any queries or support, please contact [Arsalan] at [arsalan.rex@gmail.com].