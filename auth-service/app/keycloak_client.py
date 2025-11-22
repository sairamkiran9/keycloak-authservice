from keycloak import KeycloakOpenID
from app.config import Config

class KeycloakClient:
    def __init__(self):
        self.server_url = Config.KEYCLOAK_SERVER_URL
        self.realm = Config.KEYCLOAK_REALM
        self.client_id = Config.KEYCLOAK_CLIENT_ID
        self.client_secret = Config.KEYCLOAK_CLIENT_SECRET
        
        # Initialize Keycloak OpenID Connect client
        self.keycloak_openid = KeycloakOpenID(
            server_url=self.server_url,
            client_id=self.client_id,
            realm_name=self.realm,
            client_secret_key=self.client_secret
        )
    
    def authenticate(self, username: str, password: str) -> dict:
        """
        Authenticate user with Keycloak
        Returns access_token, refresh_token, and expiration times
        """
        try:
            token = self.keycloak_openid.token(username, password)
            return {
                'success': True,
                'tokens': token
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'Authentication failed'
            }
    
    def refresh_token(self, refresh_token: str) -> dict:
        """Get new access token using refresh token"""
        try:
            token = self.keycloak_openid.refresh_token(refresh_token)
            return {
                'success': True,
                'tokens': token
            }
        except Exception:
            return {
                'success': False,
                'error': 'Token refresh failed'
            }
    
    def logout(self, refresh_token: str) -> dict:
        """Logout user and invalidate tokens"""
        try:
            self.keycloak_openid.logout(refresh_token)
            return {'success': True}
        except Exception:
            return {
                'success': False,
                'error': 'Logout failed'
            }
    
    def get_public_key(self) -> str:
        """Get realm public key for JWT verification"""
        return self.keycloak_openid.public_key()
    
    def get_user_info(self, token: str) -> dict:
        """Get user information from access token"""
        try:
            user_info = self.keycloak_openid.userinfo(token)
            return {
                'success': True,
                'user_info': user_info
            }
        except Exception:
            return {
                'success': False,
                'error': 'Failed to get user info'
            }