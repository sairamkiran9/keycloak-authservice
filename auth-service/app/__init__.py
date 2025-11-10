from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
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

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(protected_bp)

    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy', 'service': 'auth-service'}, 200

    return app