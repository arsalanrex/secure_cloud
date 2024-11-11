# Secure Cloud Storage

A secure, encrypted file storage solution that fragments and distributes encrypted data across multiple cloud storage providers including Google Drive, OneDrive, and Box.

## Features

- End-to-end file encryption using Fernet symmetric encryption
- File fragmentation for distributed storage
- Support for multiple cloud storage providers:
  - Google Drive
  - Microsoft OneDrive
  - Box
- Web-based user interface
- Secure metadata management
- Password-based key derivation

## Prerequisites

- Python 3.7+
- Flask web server
- Cloud service accounts (Google Drive, OneDrive, Box)
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd secure-cloud-storage
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

## Usage

1. Start the application:
```bash
python run.py
```

2. Access the web interface at `http://localhost:5000`

3. Log in using your preferred cloud service

4. Upload files:
   - Files are automatically encrypted
   - Split into fragments
   - Distributed across your cloud storage

5. Download files:
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

## Project Structure

```
secure-cloud-storage/
├── config.py                 # Configuration settings
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── encryption/             # Encryption modules
│   ├── encryptor.py       # Encryption implementation
│   └── fragmenter.py      # File fragmentation logic
├── cloud_services/        # Cloud provider implementations
│   ├── base_cloud.py     # Abstract base class
│   ├── gdrive_service.py # Google Drive implementation
│   ├── onedrive_service.py # OneDrive implementation
│   └── box_service.py    # Box implementation
├── utils/                 # Utility functions
│   └── metadata_manager.py # Metadata handling
└── web_interface/        # Flask web application
    ├── app.py           # Flask application setup
    ├── routes.py        # Route handlers
    └── templates/       # HTML templates
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Security Considerations

- Always use strong passwords for encryption
- Keep your cloud service credentials secure
- Don't share your encryption key
- Regularly backup your metadata
- Monitor your cloud storage usage

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This project is for educational purposes. While it implements security best practices, you should thoroughly review and test the security measures before using it in a production environment.
