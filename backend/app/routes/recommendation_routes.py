from flask import request, jsonify
from . import recommendations_bp
from app.services.recommendation_engine import RecommendationEngine
from app.utils.fpl_api import FPLAPIError, FPLResourceNotFound


def api_error_response(error):
    if isinstance(error, FPLResourceNotFound):
        return jsonify({"error": {"code": "not_found", "message": str(error), "retryable": False}}), 404
    if isinstance(error, FPLAPIError):
        return jsonify({"error": {"code": "upstream_unavailable", "message": str(error), "retryable": True}}), 502
    return jsonify({"error": {"code": "internal_error", "message": "Unexpected server error.", "retryable": False}}), 500

@recommendations_bp.route('/<int:team_id>/transfers', methods=['GET'])
def get_transfer_recommendations(team_id):
    """Get best 5 transfer options per position"""
    try:
        engine = RecommendationEngine(team_id)
        recommendations = engine.get_best_transfers_per_position()
        
        # Add debug info
        debug_info = {
            'team_id': team_id,
            'positions_with_recommendations': {
                pos: len(players) for pos, players in recommendations.items()
            }
        }
        
        return jsonify({
            'team_id': team_id,
            'recommendations': recommendations,
            '_debug': debug_info
        }), 200
    except Exception as error:
        return api_error_response(error)

@recommendations_bp.route('/<int:team_id>/differentials', methods=['GET'])
def get_differentials(team_id):
    """Get 5 high-upside differentials"""
    try:
        engine = RecommendationEngine(team_id)
        differentials = engine.get_high_upside_differentials(count=5)
        return jsonify({
            'team_id': team_id,
            'differentials': differentials
        }), 200
    except Exception as error:
        return api_error_response(error)

@recommendations_bp.route('/<int:team_id>/all', methods=['GET'])
def get_all_recommendations(team_id):
    """Get all recommendations (transfers + differentials)"""
    try:
        engine = RecommendationEngine(team_id)
        all_recs = engine.get_smart_recommendations()
        return jsonify({
            'team_id': team_id,
            'data': all_recs
        }), 200
    except Exception as error:
        return api_error_response(error)
