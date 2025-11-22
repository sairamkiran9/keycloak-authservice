import jwt
from jwt import PyJWKClient
from functools import wraps
from flask import request, jsonify
from app.config import Config
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class JWTValidator:
    def __init__(self):
        self.server_url = Config.KEYCLOAK_SERVER_URL
        self.realm = Config.KEYCLOAK_REALM
        
        # JWKS URL for public key retrieval
        self.jwks_url = f"{self.server_url}/realms/{self.realm}/protocol/openid-connect/certs"
        self.jwks_client = PyJWKClient(self.jwks_url)
    
    def decode_token(self, token: str, verify: bool = True) -> Optional[Dict[str, Any]]:
        """
        Decode and validate JWT token
        
        Args:
            token: JWT token string
            verify: Whether to verify signature and claims
            
        Returns:
            Decoded token payload or None if invalid
        """
        try:
            if verify:
                # Get signing key from JWKS
                signing_key = self.jwks_client.get_signing_key_from_jwt(token)
                
                # Decode and verify token
                decoded = jwt.decode(
                    token,
                    signing_key.key,
                    algorithms=[Config.TOKEN_ALGORITHM],
                    audience='account',
                    options={
                        'verify_signature': True,
                        'verify_exp': True,
                        'verify_nbf': True,
                        'verify_iat': True,
                        'verify_aud': True
                    }
                )
            else:
                # Decode without verification (for debugging only)
                decoded = jwt.decode(token, options={'verify_signature': False})
            
            return decoded
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token provided")
            return None
    
    def extract_claims(self, token_payload: dict) -> dict:
        """Extract important claims from token payload"""
        return {
            'user_id': token_payload.get('sub'),
            'username': token_payload.get('preferred_username'),
            'email': token_payload.get('email'),
            'roles': self._extract_roles(token_payload),
            'realm_access': token_payload.get('realm_access', {}),
            'resource_access': token_payload.get('resource_access', {}),
            'scope': token_payload.get('scope', '').split(),
            'issued_at': token_payload.get('iat'),
            'expires_at': token_payload.get('exp'),
            'issuer': token_payload.get('iss')
        }
    
    def _extract_roles(self, token_payload: dict) -> list:
        """Extract roles from token payload"""
        roles = []
        
        # Realm roles
        realm_access = token_payload.get('realm_access', {})
        roles.extend(realm_access.get('roles', []))
        
        # Client roles
        resource_access = token_payload.get('resource_access', {})
        for client, access in resource_access.items():
            client_roles = access.get('roles', [])
            roles.extend([f"{client}:{role}" for role in client_roles])
        
        return list(set(roles))

# JWT validation decorator
def jwt_required(roles: Optional[list] = None):
    """Decorator to protect routes with JWT authentication"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Extract token from Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({'error': 'Authorization header missing'}), 401
            
            try:
                # Expected format: "Bearer <token>"
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid authorization header format'}), 401
            
            # Validate token
            validator = JWTValidator()
            payload = validator.decode_token(token)
            
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Extract claims
            claims = validator.extract_claims(payload)
            
            # Check roles if specified
            if roles:
                user_roles = claims.get('roles', [])
                if not any(role in user_roles for role in roles):
                    return jsonify({'error': 'Insufficient permissions'}), 403
            
            # Attach claims to request context
            request.user_claims = claims
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator