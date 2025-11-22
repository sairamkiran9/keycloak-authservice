import pytest
from unittest.mock import patch, MagicMock
from app import create_app
import json

class TestConfig:
    TESTING = True
    KEYCLOAK_SERVER_URL = 'http://test-keycloak:8080'
    KEYCLOAK_REALM = 'test-realm'
    KEYCLOAK_CLIENT_ID = 'test-client'
    KEYCLOAK_CLIENT_SECRET = 'test-secret'
    REGISTRATION_ENABLED = True
    MIN_PASSWORD_LENGTH = 8

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        yield client

@patch('app.routes.auth.jwt_validator.decode_token')
@patch('app.routes.auth.jwt_validator.extract_claims')
@patch('app.routes.auth.keycloak_client.authenticate')
def test_login_success(mock_auth, mock_extract, mock_decode, client):
    mock_auth.return_value = {
        'success': True,
        'tokens': {
            'access_token': 'token123',
            'refresh_token': 'refresh123',
            'expires_in': 300,
            'refresh_expires_in': 1800,
            'token_type': 'Bearer'
        }
    }
    mock_decode.return_value = {'sub': 'user-123'}
    mock_extract.return_value = {
        'user_id': 'user-123',
        'username': 'user',
        'email': 'user@test.com',
        'roles': ['user']
    }

    response = client.post('/auth/login', json={'username': 'user', 'password': 'pass'})

    assert response.status_code == 200
    assert 'access_token' in response.json

@patch('app.routes.auth.keycloak_client.authenticate')
def test_login_failure(mock_auth, client):
    mock_auth.return_value = {'success': False, 'error': 'Invalid credentials'}

    response = client.post('/auth/login', json={'username': 'user', 'password': 'wrong'})

    assert response.status_code == 401

@patch('app.routes.auth.keycloak_client.refresh_token')
def test_refresh_success(mock_refresh, client):
    mock_refresh.return_value = {
        'success': True,
        'tokens': {
            'access_token': 'new_token',
            'refresh_token': 'new_refresh',
            'expires_in': 300,
            'refresh_expires_in': 1800,
            'token_type': 'Bearer'
        }
    }

    response = client.post('/auth/refresh', json={'refresh_token': 'refresh123'})

    assert response.status_code == 200
    assert 'access_token' in response.json

@patch('app.routes.auth.keycloak_client.logout')
def test_logout_success(mock_logout, client):
    mock_logout.return_value = {'success': True}

    response = client.post('/auth/logout', json={'refresh_token': 'refresh123'})

    assert response.status_code == 200

def test_validate_missing_token(client):
    response = client.post('/auth/validate', json={})
    # flask-smorest returns 422 for validation errors
    assert response.status_code == 422

def test_public_endpoint(client):
    response = client.get('/api/public')
    assert response.status_code == 200

def test_protected_endpoint_no_auth(client):
    response = client.get('/api/protected')
    assert response.status_code == 401
