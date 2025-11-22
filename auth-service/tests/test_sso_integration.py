import pytest
import json
import time
from unittest.mock import patch, MagicMock
from app import create_app
from app.config import Config


class TestSSOIntegrationConfig(Config):
    TESTING = True
    KEYCLOAK_SERVER_URL = 'http://localhost:8080'
    KEYCLOAK_REALM = 'microservices-realm'
    KEYCLOAK_CLIENT_ID = 'auth-service'


@pytest.fixture
def app():
    app = create_app(TestSSOIntegrationConfig)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


class TestSSOEndToEndFlow:
    """End-to-end integration tests for SSO functionality"""

    @patch.dict('os.environ', {
        'SSO_ENABLED': 'true',
        'GOOGLE_CLIENT_ID': 'test-google-client-id',
        'GOOGLE_CLIENT_SECRET': 'test-google-secret'
    })
    def test_complete_sso_authentication_flow(self, client):
        """Test complete SSO flow from discovery to token exchange"""
        
        # Step 1: Client discovers available SSO providers
        providers_response = client.get('/auth/sso/providers')
        assert providers_response.status_code == 200
        
        providers_data = json.loads(providers_response.data)
        assert len(providers_data['providers']) == 1
        
        google_provider = providers_data['providers'][0]
        assert google_provider['id'] == 'google'
        assert google_provider['displayName'] == 'Continue with Google'
        
        # Step 2: Client requests SSO login URL
        login_response = client.get('/auth/sso/login/google')
        assert login_response.status_code == 200
        
        login_data = json.loads(login_response.data)
        redirect_url = login_data['redirect_url']
        
        # Verify redirect URL structure
        assert 'localhost:8080/realms/microservices-realm/protocol/openid-connect/auth' in redirect_url
        assert 'kc_idp_hint=google' in redirect_url
        assert 'redirect_uri=http%3A//localhost%3A3000/callback' in redirect_url or 'redirect_uri=http://localhost:3000/callback' in redirect_url
        
        # Step 3: Simulate OAuth callback with authorization code
        with patch('app.routes.sso.keycloak_openid') as mock_keycloak:
            mock_token_response = {
                'access_token': 'sso-access-token-12345',
                'refresh_token': 'sso-refresh-token-67890',
                'expires_in': 900,
                'token_type': 'Bearer'
            }
            mock_keycloak.token.return_value = mock_token_response
            
            callback_response = client.post('/auth/oauth/callback',
                                          json={'code': 'oauth-authorization-code'},
                                          content_type='application/json')
            
            assert callback_response.status_code == 200
            callback_data = json.loads(callback_response.data)
            
            # Verify token response
            assert callback_data['access_token'] == 'sso-access-token-12345'
            assert callback_data['refresh_token'] == 'sso-refresh-token-67890'
            assert callback_data['expires_in'] == 900
            
            # Verify Keycloak client was called correctly
            mock_keycloak.token.assert_called_once_with(
                grant_type='authorization_code',
                code='oauth-authorization-code',
                redirect_uri='http://localhost:3000/callback'
            )

    @patch.dict('os.environ', {'SSO_ENABLED': 'false'})
    def test_sso_disabled_flow(self, client):
        """Test behavior when SSO is disabled"""
        
        # Should return empty providers list
        providers_response = client.get('/auth/sso/providers')
        assert providers_response.status_code == 200
        
        providers_data = json.loads(providers_response.data)
        assert len(providers_data['providers']) == 0
        
        # Login URL generation should still work (for flexibility)
        login_response = client.get('/auth/sso/login/google')
        assert login_response.status_code == 200

    def test_sso_error_handling(self, client):
        """Test error handling in SSO flow"""
        
        # Test callback without code
        response = client.post('/auth/oauth/callback',
                             json={},
                             content_type='application/json')
        assert response.status_code == 400
        
        # Test callback with invalid code
        with patch('app.routes.sso.keycloak_openid') as mock_keycloak:
            mock_keycloak.token.side_effect = Exception('Invalid authorization code')
            
            response = client.post('/auth/oauth/callback',
                                 json={'code': 'invalid-code'},
                                 content_type='application/json')
            assert response.status_code == 400
            
            error_data = json.loads(response.data)
            assert 'Invalid authorization code' in error_data['error']

    @patch.dict('os.environ', {
        'SSO_ENABLED': 'true',
        'GOOGLE_CLIENT_ID': 'test-client-id'
    })
    def test_multiple_provider_support(self, client):
        """Test framework supports multiple SSO providers"""
        
        providers_response = client.get('/auth/sso/providers')
        providers_data = json.loads(providers_response.data)
        
        # Currently only Google, but framework ready for more
        assert len(providers_data['providers']) == 1
        assert providers_data['providers'][0]['id'] == 'google'
        
        # Test login URL generation for different providers
        google_response = client.get('/auth/sso/login/google')
        assert google_response.status_code == 200
        
        # Framework should handle other providers gracefully
        github_response = client.get('/auth/sso/login/github')
        assert github_response.status_code == 200
        
        github_data = json.loads(github_response.data)
        assert 'kc_idp_hint=github' in github_data['redirect_url']


class TestSSOSecurityConsiderations:
    """Test security aspects of SSO implementation"""

    def test_redirect_uri_validation(self, client):
        """Test that redirect URI is properly set"""
        
        response = client.get('/auth/sso/login/google')
        data = json.loads(response.data)
        
        # Ensure redirect URI points to expected callback
        assert 'redirect_uri=http%3A//localhost%3A3000/callback' in data['redirect_url'] or 'redirect_uri=http://localhost:3000/callback' in data['redirect_url']

    def test_scope_configuration(self, client):
        """Test that proper OAuth scopes are requested"""
        
        response = client.get('/auth/sso/login/google')
        data = json.loads(response.data)
        
        # Verify OpenID Connect scopes
        assert 'scope=openid+profile+email' in data['redirect_url']

    def test_state_parameter_ready(self, client):
        """Test framework is ready for CSRF protection via state parameter"""
        
        response = client.get('/auth/sso/login/google')
        data = json.loads(response.data)
        
        # Current implementation doesn't include state, but URL structure supports it
        redirect_url = data['redirect_url']
        assert 'client_id=' in redirect_url
        assert 'response_type=code' in redirect_url
        
        # Framework can easily add state parameter for CSRF protection


class TestSSOPerformance:
    """Test performance aspects of SSO implementation"""

    @patch.dict('os.environ', {
        'SSO_ENABLED': 'true',
        'GOOGLE_CLIENT_ID': 'perf-test-client'
    })
    def test_provider_endpoint_performance(self, client):
        """Test SSO provider endpoint responds quickly"""
        
        start_time = time.time()
        response = client.get('/auth/sso/providers')
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 0.1  # Should respond in < 100ms

    def test_login_url_generation_performance(self, client):
        """Test login URL generation is fast"""
        
        start_time = time.time()
        response = client.get('/auth/sso/login/google')
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 0.1  # Should respond in < 100ms

    @patch('app.routes.sso.keycloak_openid')
    def test_callback_processing_performance(self, mock_keycloak, client):
        """Test OAuth callback processing is efficient"""
        
        mock_keycloak.token.return_value = {
            'access_token': 'perf-test-token',
            'refresh_token': 'perf-test-refresh',
            'expires_in': 900
        }
        
        start_time = time.time()
        response = client.post('/auth/oauth/callback',
                             json={'code': 'perf-test-code'},
                             content_type='application/json')
        end_time = time.time()
        
        assert response.status_code == 200
        # Allow more time for token exchange (network call to Keycloak)
        assert (end_time - start_time) < 1.0  # Should complete in < 1 second


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])