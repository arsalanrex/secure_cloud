import os
import pytest
from web_interface.app import app  # Adjusted import for app
from encryption.encryptor import Encryptor  # Adjusted import for Encryptor
from encryption.fragmenter import Fragmenter  # Adjusted import for Fragmenter

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login_page(client):
    """Test if login page loads correctly"""
    rv = client.get('/login')
    assert rv.status_code == 200
    assert b'Secure Cloud Storage' in rv.data

def test_encryption():
    """Test encryption and decryption"""
    encryptor = Encryptor("test_password")
    test_data = b"Hello, World!"
    encrypted = encryptor.encrypt(test_data)
    decrypted = encryptor.decrypt(encrypted)
    assert test_data == decrypted

def test_fragmentation():
    """Test file fragmentation and reconstruction"""
    fragmenter = Fragmenter(fragment_size=5)  # Small size for testing
    test_data = b"Hello, World!"
    fragments = fragmenter.fragment_file(test_data)
    reconstructed = fragmenter.reconstruct_file(fragments)
    assert test_data == reconstructed

def test_protected_routes(client):
    """Test if protected routes redirect to login"""
    rv = client.get('/dashboard')
    assert rv.status_code == 302  # Should redirect to login
    assert '/login' in rv.location

if __name__ == '__main__':
    pytest.main(['-v'])
