from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_smorest import Api
from app.config import Config

# Initialize limiter globally
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Swagger/OpenAPI configuration
    app.config['API_TITLE'] = 'Keycloak Auth Service API'
    app.config['API_VERSION'] = 'v1'
    app.config['OPENAPI_VERSION'] = '3.0.2'
    app.config['OPENAPI_URL_PREFIX'] = '/'
    app.config['OPENAPI_SWAGGER_UI_PATH'] = '/swagger-ui'
    app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    app.config['OPENAPI_REDOC_PATH'] = '/redoc'
    app.config['OPENAPI_REDOC_URL'] = 'https://cdn.jsdelivr.net/npm/redoc/bundles/redoc.standalone.js'

    # OpenAPI Security Scheme for Bearer JWT Authentication
    app.config['API_SPEC_OPTIONS'] = {
        'components': {
            'securitySchemes': {
                'bearerAuth': {
                    'type': 'http',
                    'scheme': 'bearer',
                    'bearerFormat': 'JWT',
                    'description': 'Enter JWT token obtained from /auth/login'
                }
            }
        }
    }

    # Initialize API
    api = Api(app)

    # Initialize rate limiter
    limiter.init_app(app)

    # Enable CORS for all routes
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    # Import blueprints here to avoid circular imports
    from app.routes.auth import auth_bp
    from app.routes.protected import protected_bp
    from app.routes.sso import sso_bp

    # Register blueprints with API
    api.register_blueprint(auth_bp)
    api.register_blueprint(protected_bp)
    api.register_blueprint(sso_bp)

    # Custom error handler for validation errors (422)
    @app.errorhandler(422)
    def handle_validation_error(err):
        """Convert flask-smorest validation errors to user-friendly format"""
        messages = err.data.get("messages", {})
        json_errors = messages.get("json", {})

        # Check if request had no JSON body (Content-Type check)
        from flask import request
        if not request.is_json or request.get_json(silent=True) is None:
            return jsonify({"error": "JSON body required"}), 422

        # Map field names to user-friendly error messages
        field_messages = {
            "code": "Authorization code required",
            "token": "Token required",
            "refresh_token": "Refresh token required",
            "username": "Username required",
            "password": "Password required",
            "email": "Valid email required",
        }

        # Check for specific field errors and return friendly message
        for field, friendly_msg in field_messages.items():
            if field in json_errors:
                return jsonify({"error": friendly_msg}), 422

        # Default: return generic validation error with details
        return jsonify({
            "error": "Validation error",
            "details": json_errors if json_errors else messages
        }), 422

    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return {'status': 'healthy', 'service': 'auth-service'}, 200

    return app