import pytest
from unittest.mock import patch, Mock
from app import create_app
import json

class TestConfig:
    TESTING = True
    KEYCLOAK_SERVER_URL = 'http://test-keycloak:8080'
    KEYCLOAK_REALM = 'test-realm'
    KEYCLOAK_CLIENT_ID = 'test-client'
    KEYCLOAK_CLIENT_SECRET = 'test-secret'

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_tokens():
    return {
        'access_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.test',
        'refresh_token': 'refresh_token_123',
        'expires_in': 300,
        'refresh_expires_in': 1800,
        'token_type': 'Bearer'
    }

class TestLoginLogoutFlow:
    
    @patch('app.routes.auth.keycloak_client.authenticate')
    @patch('app.routes.auth.jwt_validator.decode_token')
    def test_login_logout_flow(self, mock_decode, mock_auth, client, mock_tokens):
        # Mock successful login
        mock_auth.return_value = {'success': True, 'tokens': mock_tokens}
        mock_decode.return_value = {
            'sub': 'user-123',
            'preferred_username': 'testuser',
            'email': 'test@example.com'
        }
        
        # Login
        login_response = client.post('/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        
        assert login_response.status_code == 200
        login_data = login_response.json
        access_token = login_data['access_token']
        refresh_token = login_data['refresh_token']
        
        # Mock logout
        with patch('app.routes.auth.keycloak_client.logout') as mock_logout:
            mock_logout.return_value = {'success': True}
            
            logout_response = client.post('/auth/logout', json={
                'refresh_token': refresh_token
            })
            
            assert logout_response.status_code == 200

class TestTokenRefreshFlow:
    
    @patch('app.routes.auth.keycloak_client.refresh_token')
    def test_token_refresh_flow(self, mock_refresh, client, mock_tokens):
        # Mock successful refresh
        new_tokens = mock_tokens.copy()
        new_tokens['access_token'] = 'new_access_token'
        mock_refresh.return_value = {'success': True, 'tokens': new_tokens}
        
        response = client.post('/auth/refresh', json={
            'refresh_token': 'refresh_token_123'
        })
        
        assert response.status_code == 200
        assert response.json['access_token'] == 'new_access_token'
    
    @patch('app.routes.auth.keycloak_client.refresh_token')
    def test_refresh_with_invalid_token(self, mock_refresh, client):
        mock_refresh.return_value = {'success': False, 'error': 'Invalid refresh token'}
        
        response = client.post('/auth/refresh', json={
            'refresh_token': 'invalid_token'
        })
        
        assert response.status_code == 401

class TestProtectedEndpointFlow:
    
    @patch('app.utils.jwt_utils.JWTValidator.decode_token')
    @patch('app.utils.jwt_utils.JWTValidator.extract_claims')
    def test_protected_endpoint_with_valid_token(self, mock_extract, mock_decode, client):
        mock_decode.return_value = {'sub': 'user-123'}
        mock_extract.return_value = {
            'user_id': 'user-123',
            'username': 'testuser',
            'roles': ['user']
        }
        
        response = client.get('/api/protected', headers={
            'Authorization': 'Bearer valid_token'
        })
        
        assert response.status_code == 200
        assert 'testuser' in response.json['authenticated_user']