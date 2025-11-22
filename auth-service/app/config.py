import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    
    # Keycloak
    KEYCLOAK_SERVER_URL = os.getenv('KEYCLOAK_SERVER_URL', 'http://localhost:8080')
    KEYCLOAK_REALM = os.getenv('KEYCLOAK_REALM', 'microservices-realm')
    KEYCLOAK_CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID', 'auth-service')
    KEYCLOAK_CLIENT_SECRET = os.getenv('KEYCLOAK_CLIENT_SECRET', '')

    # Keycloak Admin credentials (for user management)
    KEYCLOAK_ADMIN = os.getenv('KEYCLOAK_ADMIN') or 'admin'
    KEYCLOAK_ADMIN_PASSWORD = os.getenv('KEYCLOAK_ADMIN_PASSWORD') or 'admin'

    # Registration settings
    REGISTRATION_ENABLED = os.getenv('REGISTRATION_ENABLED', 'true').lower() == 'true'
    MIN_PASSWORD_LENGTH = int(os.getenv('MIN_PASSWORD_LENGTH', '8'))
    
    # Token
    TOKEN_ALGORITHM = 'RS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 15
    REFRESH_TOKEN_EXPIRE_MINUTES = 30
    
    # Client Store
    CLIENT_STORE_PATH = 'data/clients.json'