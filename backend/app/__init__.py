from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Enable CORS for all routes with proper configuration
    cors_config = {
        "origins": ["http://localhost:3000", "http://localhost:5000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
    CORS(app, resources={r"/api/*": cors_config})
    
    # Configuration
    app.config['ENV'] = os.getenv('FLASK_ENV', 'development')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', False)
    
    # Register blueprints
    from app.routes import team_bp, recommendations_bp, photos_bp
    app.register_blueprint(team_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(photos_bp)
    
    return app
