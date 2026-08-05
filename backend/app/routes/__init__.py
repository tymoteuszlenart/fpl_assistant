from flask import Blueprint

team_bp = Blueprint('team', __name__, url_prefix='/api/team')
recommendations_bp = Blueprint('recommendations', __name__, url_prefix='/api/recommendations')
photos_bp = Blueprint('photos', __name__, url_prefix='/api/photos')
tracked_teams_bp = Blueprint('tracked_teams', __name__, url_prefix='/api/tracked-teams')

# Import routes to register them
from . import team_routes, recommendation_routes, photo_routes, tracked_team_routes
