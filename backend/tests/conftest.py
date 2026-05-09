import pytest
import tempfile
import os
from app import app as flask_app

@pytest.fixture
def app():
    """Create and configure a test Flask app"""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    flask_app.config.update({
        'TESTING': True,
        'DATABASE_PATH': db_path,
        'SECRET_KEY': 'test-secret-key'
    })
    
    yield flask_app
    
    # Clean up
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Create a test client for the Flask app"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test runner for CLI commands"""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers(client):
    """Get authentication headers with valid JWT token"""
    # Login with test credentials
    response = client.post('/authentication/login', json={
        'email': 'admin@example.com',
        'password': 'newpassword456'
    })
    
    if response.status_code == 200:
        token = response.json['access_token']
        return {'Authorization': f'Bearer {token}'}
    return {}

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'testpassword123'
    } 