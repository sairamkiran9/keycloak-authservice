from flask import jsonify, request
from flask_smorest import Blueprint
from app.config import Config
from app.keycloak_client import KeycloakClient
from app.schemas import (
    SSOProvidersResponseSchema, SSOLoginResponseSchema,
    OAuthCallbackRequestSchema, OAuthCallbackResponseSchema, ErrorResponseSchema
)
from urllib.parse import urlencode
import os

# Initialize Keycloak client
keycloak_client = KeycloakClient()
keycloak_openid = keycloak_client.keycloak_openid

sso_bp = Blueprint('sso', 'sso', url_prefix='/auth', description='SSO authentication endpoints')

@sso_bp.route('/sso/providers', methods=['GET'])
@sso_bp.response(200, SSOProvidersResponseSchema)
def get_sso_providers():
    """Get list of available SSO providers"""
    providers = []

    if os.getenv('SSO_ENABLED') == 'true':
        if os.getenv('GOOGLE_CLIENT_ID'):
            providers.append({
                'id': 'google',
                'name': 'Google',
                'displayName': 'Continue with Google'
            })

    return jsonify({'providers': providers})

@sso_bp.route('/sso/login/<provider>', methods=['GET'])
@sso_bp.response(200, SSOLoginResponseSchema)
@sso_bp.response(400, ErrorResponseSchema)
def sso_login(provider):
    """Generate SSO login URL for provider
    
    Args:
        provider: SSO provider ID (e.g., 'google')
    """
    keycloak_url = Config.KEYCLOAK_SERVER_URL
    realm = Config.KEYCLOAK_REALM
    client_id = Config.KEYCLOAK_CLIENT_ID

    # For Docker, map internal keycloak:8080 to localhost:8080 for browser
    auth_endpoint = f"{keycloak_url.replace('keycloak:8080', 'localhost:8080')}/realms/{realm}/protocol/openid-connect/auth"

    params = {
        'client_id': client_id,
        'redirect_uri': 'http://localhost:3000/callback',
        'response_type': 'code',
        'scope': 'openid profile email',
        'kc_idp_hint': provider  # Tells Keycloak to use this IdP
    }

    redirect_url = f"{auth_endpoint}?{urlencode(params)}"

    return jsonify({'redirect_url': redirect_url})

@sso_bp.route('/oauth/callback', methods=['POST'])
@sso_bp.arguments(OAuthCallbackRequestSchema)
@sso_bp.response(200, OAuthCallbackResponseSchema)
@sso_bp.response(400, ErrorResponseSchema)
def oauth_callback(json_data):
    """Exchange OAuth authorization code for tokens"""

    data = json_data
    code = data['code']

    try:
        # Exchange code for token
        token_response = keycloak_openid.token(
            grant_type='authorization_code',
            code=code,
            redirect_uri='http://localhost:3000/callback'
        )

        return jsonify({
            'access_token': token_response['access_token'],
            'refresh_token': token_response['refresh_token'],
            'expires_in': token_response['expires_in']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400