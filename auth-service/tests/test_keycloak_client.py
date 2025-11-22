import pytest
from unittest.mock import Mock, patch, MagicMock
from app.keycloak_client import KeycloakClient

class TestKeycloakClient:

    @pytest.fixture
    def mock_keycloak_openid(self):
        """Create a mock KeycloakOpenID instance"""
        return MagicMock()

    @pytest.fixture
    def client(self, mock_keycloak_openid):
        """Create a KeycloakClient with mocked keycloak_openid"""
        with patch('app.keycloak_client.KeycloakOpenID', return_value=mock_keycloak_openid):
            client = KeycloakClient()
        return client

    def test_authenticate_success(self, client):
        """Test successful authentication"""
        client.keycloak_openid.token.return_value = {'access_token': 'token123'}

        result = client.authenticate('user', 'pass')

        assert result['success'] is True
        assert 'tokens' in result
        client.keycloak_openid.token.assert_called_once_with('user', 'pass')

    def test_authenticate_failure(self, client):
        """Test authentication failure"""
        client.keycloak_openid.token.side_effect = Exception('Auth failed')

        result = client.authenticate('user', 'wrong')

        assert result['success'] is False
        assert 'error' in result

    def test_refresh_token_success(self, client):
        """Test successful token refresh"""
        client.keycloak_openid.refresh_token.return_value = {'access_token': 'new_token'}

        result = client.refresh_token('refresh123')

        assert result['success'] is True
        assert 'tokens' in result
        client.keycloak_openid.refresh_token.assert_called_once_with('refresh123')

    def test_refresh_token_failure(self, client):
        """Test token refresh failure"""
        client.keycloak_openid.refresh_token.side_effect = Exception('Refresh failed')

        result = client.refresh_token('invalid_refresh')

        assert result['success'] is False
        assert 'error' in result

    def test_logout_success(self, client):
        """Test successful logout"""
        client.keycloak_openid.logout.return_value = None

        result = client.logout('refresh123')

        assert result['success'] is True
        client.keycloak_openid.logout.assert_called_once_with('refresh123')

    def test_logout_failure(self, client):
        """Test logout failure"""
        client.keycloak_openid.logout.side_effect = Exception('Logout failed')

        result = client.logout('invalid_refresh')

        assert result['success'] is False
        assert 'error' in result
