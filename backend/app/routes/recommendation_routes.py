from flask import request, jsonify
from . import recommendations_bp
from app.services.recommendation_engine import RecommendationEngine

@recommendations_bp.route('/<int:team_id>/transfers', methods=['GET'])
def get_transfer_recommendations(team_id):
    """Get best 5 transfer options per position"""
    try:
        engine = RecommendationEngine(team_id)
        recommendations = engine.get_best_transfers_per_position()
        return jsonify({
            'team_id': team_id,
            'recommendations': recommendations
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    except Exception as e:
        return jsonify({'error': str(e)}), 500
