from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.routes.auth import auth_bp
from app.routes.protected import protected_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS for all routes
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(protected_bp)

    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy', 'service': 'auth-service'}, 200

    return app