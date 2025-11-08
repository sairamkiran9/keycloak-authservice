import pytest
from app import create_app
import json

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login_success(client):
    """Test successful login"""
    response = client.post('/auth/login',
        data=json.dumps({
            'username': 'testuser',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert 'refresh_token' in data

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post('/auth/login',
        data=json.dumps({
            'username': 'wronguser',
            'password': 'wrongpass'
        }),
        content_type='application/json'
    )
    assert response.status_code == 401

def test_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without token"""
    response = client.get('/api/protected')
    assert response.status_code == 401

def test_public_endpoint_no_auth(client):
    """Test public endpoint requires no auth"""
    response = client.get('/api/public')
    assert response.status_code == 200