import pytest
from unittest.mock import Mock, patch
import jwt
from app.utils.jwt_utils import JWTValidator, jwt_required
from flask import Flask

class TestJWTValidator:
    
    @pytest.fixture
    def validator(self):
        return JWTValidator()
    
    @pytest.fixture
    def mock_payload(self):
        return {
            'sub': 'user-123',
            'preferred_username': 'testuser',
            'email': 'test@example.com',
            'realm_access': {'roles': ['user']},
            'resource_access': {'client': {'roles': ['admin']}},
            'iat': 1234567890,
            'exp': 1234567990
        }
    
    def test_extract_claims(self, validator, mock_payload):
        claims = validator.extract_claims(mock_payload)
        assert claims['user_id'] == 'user-123'
        assert claims['username'] == 'testuser'
        assert 'user' in claims['roles']
    
    @patch('app.utils.jwt_utils.jwt.decode')
    def test_decode_token_success(self, mock_decode, validator, mock_payload):
        # Mock the jwks_client to return a fake signing key
        mock_signing_key = Mock()
        mock_signing_key.key = 'fake-key'
        validator.jwks_client = Mock()
        validator.jwks_client.get_signing_key_from_jwt.return_value = mock_signing_key

        mock_decode.return_value = mock_payload
        result = validator.decode_token('valid.token')
        assert result == mock_payload
    
    @patch('app.utils.jwt_utils.jwt.decode')
    def test_decode_token_expired(self, mock_decode, validator):
        mock_decode.side_effect = jwt.ExpiredSignatureError()
        result = validator.decode_token('expired.token')
        assert result is None

class TestJWTDecorator:
    
    @pytest.fixture
    def app(self):
        return Flask(__name__)
    
    def test_missing_auth_header(self, app):
        with app.test_request_context():
            @jwt_required()
            def view():
                return 'ok'
            response, status = view()
            assert status == 401
    
    @patch('app.utils.jwt_utils.JWTValidator.decode_token')
    def test_invalid_token(self, mock_decode, app):
        mock_decode.return_value = None
        with app.test_request_context(headers={'Authorization': 'Bearer invalid'}):
            @jwt_required()
            def view():
                return 'ok'
            response, status = view()
            assert status == 401