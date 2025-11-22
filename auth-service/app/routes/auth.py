from flask import request, jsonify
from flask_smorest import Blueprint
from app.keycloak_client import KeycloakClient
from app.utils.jwt_utils import JWTValidator, jwt_required
from app.utils.validators import validate_registration_data
from app.config import Config
from app.schemas import (
    LoginRequestSchema, LoginResponseSchema, RefreshTokenRequestSchema,
    RefreshTokenResponseSchema, LogoutRequestSchema, LogoutResponseSchema,
    ValidateTokenRequestSchema, ValidateTokenResponseSchema, UserInfoResponseSchema,
    RegisterRequestSchema, RegisterResponseSchema, ErrorResponseSchema
)
import json
import os

# Lazy import for KeycloakAdminClient to avoid connection issues
_keycloak_admin = None

def get_keycloak_admin():
    global _keycloak_admin
    if _keycloak_admin is None:
        from app.keycloak_admin_client import KeycloakAdminClient
        _keycloak_admin = KeycloakAdminClient()
    return _keycloak_admin

# Import limiter for rate limiting
from app import limiter

auth_bp = Blueprint('auth', 'auth', url_prefix='/auth', description='Authentication endpoints')
keycloak_client = KeycloakClient()
jwt_validator = JWTValidator()

# Load client store
def load_clients():
    try:
        with open('data/clients.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'clients': []}

def save_client(client_data):
    clients = load_clients()
    clients['clients'].append(client_data)
    os.makedirs('data', exist_ok=True)
    with open('data/clients.json', 'w') as f:
        json.dump(clients, f, indent=2)

@auth_bp.route('/login', methods=['POST'])
@auth_bp.arguments(LoginRequestSchema)
@auth_bp.response(200, LoginResponseSchema)
@auth_bp.response(400, ErrorResponseSchema)
@auth_bp.response(401, ErrorResponseSchema)
def login(json_data):
    """Login with username and password"""
    data = json_data
    
    # Authenticate with Keycloak
    result = keycloak_client.authenticate(
        username=data['username'],
        password=data['password']
    )
    
    if not result['success']:
        return jsonify({'error': 'Authentication failed', 'details': result['error']}), 401
    
    tokens = result['tokens']
    
    # Decode token to extract user info
    access_token = tokens['access_token']
    payload = jwt_validator.decode_token(access_token)
    claims = jwt_validator.extract_claims(payload)
    
    # Store client info (for testing purposes)
    client_info = {
        'username': data['username'],
        'user_id': claims['user_id'],
        'email': claims['email'],
        'roles': claims['roles']
    }
    save_client(client_info)
    
    return jsonify({
        'message': 'Login successful',
        'access_token': tokens['access_token'],
        'refresh_token': tokens['refresh_token'],
        'expires_in': tokens['expires_in'],
        'refresh_expires_in': tokens['refresh_expires_in'],
        'token_type': tokens['token_type'],
        'user_info': claims
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@auth_bp.arguments(RefreshTokenRequestSchema)
@auth_bp.response(200, RefreshTokenResponseSchema)
@auth_bp.response(400, ErrorResponseSchema)
@auth_bp.response(401, ErrorResponseSchema)
def refresh(json_data):
    """Refresh access token using refresh token"""
    data = json_data
    
    # Refresh token with Keycloak
    result = keycloak_client.refresh_token(data['refresh_token'])
    
    if not result['success']:
        return jsonify({'error': 'Token refresh failed', 'details': result['error']}), 401
    
    tokens = result['tokens']
    
    return jsonify({
        'message': 'Token refreshed successfully',
        'access_token': tokens['access_token'],
        'refresh_token': tokens['refresh_token'],
        'expires_in': tokens['expires_in'],
        'refresh_expires_in': tokens['refresh_expires_in'],
        'token_type': tokens['token_type']
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@auth_bp.arguments(LogoutRequestSchema)
@auth_bp.response(200, LogoutResponseSchema)
@auth_bp.response(400, ErrorResponseSchema)
def logout(json_data):
    """Logout user and invalidate tokens"""
    data = json_data
    
    result = keycloak_client.logout(data['refresh_token'])
    
    if not result['success']:
        return jsonify({'error': 'Logout failed', 'details': result['error']}), 400
    
    return jsonify({'message': 'Logout successful'}), 200

@auth_bp.route('/validate', methods=['POST'])
@auth_bp.arguments(ValidateTokenRequestSchema)
@auth_bp.response(200, ValidateTokenResponseSchema)
@auth_bp.response(400, ErrorResponseSchema)
@auth_bp.response(401, ErrorResponseSchema)
def validate(json_data):
    """Validate access token"""
    data = json_data
    
    # Decode and validate token
    payload = jwt_validator.decode_token(data['token'])
    
    if not payload:
        return jsonify({'valid': False, 'error': 'Invalid or expired token'}), 401
    
    claims = jwt_validator.extract_claims(payload)
    
    return jsonify({
        'valid': True,
        'claims': claims
    }), 200

@auth_bp.route('/userinfo', methods=['GET'])
@auth_bp.doc(security=[{"bearerAuth": []}])
@auth_bp.response(200, UserInfoResponseSchema)
@auth_bp.response(401, ErrorResponseSchema)
@jwt_required()
def userinfo():
    """Get current user information from token"""
    return jsonify({
        'user_info': request.user_claims
    }), 200

@auth_bp.route('/register', methods=['POST'])
@auth_bp.arguments(RegisterRequestSchema)
@auth_bp.response(201, RegisterResponseSchema)
@auth_bp.response(400, ErrorResponseSchema)
@auth_bp.response(403, ErrorResponseSchema)
@auth_bp.response(409, ErrorResponseSchema)
@auth_bp.response(500, ErrorResponseSchema)
@limiter.limit("5 per 15 minutes")  # Max 5 registrations per 15 minutes per IP
def register(json_data):
    """Register new user
    
    Rate limited: 5 registrations per 15 minutes per IP
    """
    # Check if registration is enabled
    if not Config.REGISTRATION_ENABLED:
        return jsonify({'error': 'Registration is currently disabled'}), 403

    data = json_data

    # Validate input data
    validation_result = validate_registration_data(data, Config.MIN_PASSWORD_LENGTH)

    if not validation_result['valid']:
        return jsonify({
            'error': 'Validation failed',
            'details': validation_result['errors']
        }), 400

    sanitized_data = validation_result['sanitized_data']

    # Get admin client
    try:
        keycloak_admin = get_keycloak_admin()
    except Exception as e:
        return jsonify({'error': f'Failed to initialize registration service: {str(e)}'}), 500

    # Register user in Keycloak
    result = keycloak_admin.register_user(
        username=sanitized_data['username'],
        email=sanitized_data['email'],
        password=sanitized_data['password'],
        first_name=sanitized_data.get('firstName', ''),
        last_name=sanitized_data.get('lastName', '')
    )

    if not result['success']:
        # Check if it's a duplicate user error
        if 'field' in result:
            return jsonify({
                'error': result['error'],
                'field': result['field']
            }), 409  # Conflict

        return jsonify({'error': result['error']}), 500

    # Return success response
    return jsonify({
        'message': 'Registration successful',
        'username': result['username'],
        'email': result['email']
    }), 201