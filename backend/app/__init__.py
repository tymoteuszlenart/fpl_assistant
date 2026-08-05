from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

def create_app(test_config=None):
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
    app.config['DATABASE'] = os.getenv(
        'FPL_ASSISTANT_DATABASE',
        os.path.join(app.instance_path, 'fpl_assistant.sqlite3'),
    )
    if test_config:
        app.config.update(test_config)

    database_directory = os.path.dirname(app.config['DATABASE'])
    if database_directory:
        os.makedirs(database_directory, exist_ok=True)
    from app.services.tracked_team_store import initialize_database
    initialize_database(app.config['DATABASE'])
    
    # Register blueprints
    from app.routes import team_bp, recommendations_bp, photos_bp, tracked_teams_bp
    app.register_blueprint(team_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(photos_bp)
    app.register_blueprint(tracked_teams_bp)
    
    return app
