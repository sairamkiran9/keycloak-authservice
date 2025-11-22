import pytest
import json
from unittest.mock import patch, MagicMock
from app import create_app
from app.config import Config


class TestConfig(Config):
    TESTING = True
    KEYCLOAK_SERVER_URL = 'http://localhost:8080'
    KEYCLOAK_REALM = 'microservices-realm'
    KEYCLOAK_CLIENT_ID = 'auth-service'


@pytest.fixture
def app():
    app = create_app(TestConfig)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


class TestSSOProviders:
    """Test SSO provider endpoints"""

    @patch.dict('os.environ', {'SSO_ENABLED': 'true', 'GOOGLE_CLIENT_ID': 'test-google-id'})
    def test_get_sso_providers_enabled(self, client):
        """Test SSO providers when enabled with Google"""
        response = client.get('/auth/sso/providers')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'providers' in data
        assert len(data['providers']) == 1
        assert data['providers'][0]['id'] == 'google'
        assert data['providers'][0]['name'] == 'Google'
        assert data['providers'][0]['displayName'] == 'Continue with Google'

    @patch.dict('os.environ', {'SSO_ENABLED': 'false'})
    def test_get_sso_providers_disabled(self, client):
        """Test SSO providers when disabled"""
        response = client.get('/auth/sso/providers')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'providers' in data
        assert len(data['providers']) == 0

    @patch.dict('os.environ', {'SSO_ENABLED': 'true'}, clear=True)
    def test_get_sso_providers_no_google_client(self, client):
        """Test SSO providers when enabled but no Google client ID"""
        response = client.get('/auth/sso/providers')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'providers' in data
        assert len(data['providers']) == 0


class TestSSOLogin:
    """Test SSO login URL generation"""

    def test_sso_login_google(self, client):
        """Test Google SSO login URL generation"""
        response = client.get('/auth/sso/login/google')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'redirect_url' in data
        redirect_url = data['redirect_url']
        
        # Verify URL components
        assert 'localhost:8080/realms/microservices-realm/protocol/openid-connect/auth' in redirect_url
        assert 'client_id=auth-service' in redirect_url
        from urllib.parse import unquote
        decoded_url = unquote(redirect_url)
        assert 'redirect_uri=http://localhost:3000/callback' in decoded_url
        assert 'response_type=code' in redirect_url
        assert 'scope=openid+profile+email' in redirect_url
        assert 'kc_idp_hint=google' in redirect_url

    def test_sso_login_invalid_provider(self, client):
        """Test SSO login with invalid provider"""
        response = client.get('/auth/sso/login/invalid')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should still generate URL but with invalid provider hint
        assert 'redirect_url' in data
        assert 'kc_idp_hint=invalid' in data['redirect_url']


class TestOAuthCallback:
    """Test OAuth callback handling"""

    @patch('app.routes.sso.keycloak_openid')
    def test_oauth_callback_success(self, mock_keycloak_openid, client):
        """Test successful OAuth callback"""
        # Mock token response
        mock_token_response = {
            'access_token': 'test-access-token',
            'refresh_token': 'test-refresh-token',
            'expires_in': 900
        }
        mock_keycloak_openid.token.return_value = mock_token_response
        
        response = client.post('/auth/oauth/callback', 
                             json={'code': 'test-auth-code'},
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['access_token'] == 'test-access-token'
        assert data['refresh_token'] == 'test-refresh-token'
        assert data['expires_in'] == 900
        
        # Verify keycloak_openid.token was called correctly
        mock_keycloak_openid.token.assert_called_once_with(
            grant_type='authorization_code',
            code='test-auth-code',
            redirect_uri='http://localhost:3000/callback'
        )

    def test_oauth_callback_missing_code(self, client):
        """Test OAuth callback without authorization code"""
        response = client.post('/auth/oauth/callback', 
                             json={},
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Authorization code required'

    def test_oauth_callback_no_json(self, client):
        """Test OAuth callback without JSON body"""
        response = client.post('/auth/oauth/callback')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'JSON body required'

    @patch('app.routes.sso.keycloak_openid')
    def test_oauth_callback_keycloak_error(self, mock_keycloak_openid, client):
        """Test OAuth callback with Keycloak error"""
        mock_keycloak_openid.token.side_effect = Exception('Invalid code')
        
        response = client.post('/auth/oauth/callback', 
                             json={'code': 'invalid-code'},
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid code' in data['error']


class TestSSOIntegration:
    """Integration tests for SSO flow"""

    @patch.dict('os.environ', {
        'SSO_ENABLED': 'true', 
        'GOOGLE_CLIENT_ID': 'test-google-id'
    })
    @patch('app.routes.sso.keycloak_openid')
    def test_complete_sso_flow(self, mock_keycloak_openid, client):
        """Test complete SSO flow from provider list to token exchange"""
        # Step 1: Get SSO providers
        providers_response = client.get('/auth/sso/providers')
        assert providers_response.status_code == 200
        providers_data = json.loads(providers_response.data)
        assert len(providers_data['providers']) == 1
        
        # Step 2: Get login URL
        login_response = client.get('/auth/sso/login/google')
        assert login_response.status_code == 200
        login_data = json.loads(login_response.data)
        assert 'redirect_url' in login_data
        
        # Step 3: Simulate callback with code
        mock_token_response = {
            'access_token': 'integration-test-token',
            'refresh_token': 'integration-test-refresh',
            'expires_in': 900
        }
        mock_keycloak_openid.token.return_value = mock_token_response
        
        callback_response = client.post('/auth/oauth/callback', 
                                      json={'code': 'integration-test-code'},
                                      content_type='application/json')
        
        assert callback_response.status_code == 200
        callback_data = json.loads(callback_response.data)
        assert callback_data['access_token'] == 'integration-test-token'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])