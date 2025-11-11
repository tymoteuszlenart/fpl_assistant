from flask import Blueprint

team_bp = Blueprint('team', __name__, url_prefix='/api/team')
recommendations_bp = Blueprint('recommendations', __name__, url_prefix='/api/recommendations')
photos_bp = Blueprint('photos', __name__, url_prefix='/api/photos')

# Import routes to register them
from . import team_routes, recommendation_routes, photo_routes
