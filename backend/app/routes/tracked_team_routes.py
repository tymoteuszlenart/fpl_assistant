"""HTTP routes for persisted FPL squad tracking."""

import os
from flask import current_app, jsonify
from app.routes import tracked_teams_bp
from app.routes.recommendation_routes import api_error_response
from app.services.tracked_team_store import TrackedTeamStore
from app.utils.fpl_api import FPLAPIClient


def _store():
    return TrackedTeamStore(current_app.config['DATABASE'])


@tracked_teams_bp.route('', methods=['GET'])
def list_tracked_teams():
    return jsonify({'teams': _store().list_teams()}), 200


@tracked_teams_bp.route('/<int:team_id>', methods=['GET'])
def get_tracked_team(team_id):
    team = _store().get_team(team_id)
    if not team:
        return jsonify({'error': {'code': 'not_found', 'message': 'Tracked team was not found.', 'retryable': False}}), 404
    return jsonify(team), 200


@tracked_teams_bp.route('/<int:team_id>/snapshots', methods=['GET'])
def get_snapshots(team_id):
    snapshots = _store().snapshots(team_id)
    if snapshots is None:
        return jsonify({'error': {'code': 'not_found', 'message': 'Tracked team was not found.', 'retryable': False}}), 404
    return jsonify({'snapshots': snapshots}), 200


@tracked_teams_bp.route('/<int:team_id>/snapshots/<int:gameweek>/changes', methods=['GET'])
def get_snapshot_changes(team_id, gameweek):
    changes = _store().snapshot_changes(team_id, gameweek)
    if changes is None:
        return jsonify({'error': {'code': 'not_found', 'message': 'Tracked team was not found.', 'retryable': False}}), 404
    return jsonify(changes), 200


@tracked_teams_bp.route('/<int:team_id>/refresh', methods=['POST'])
def refresh_tracked_team(team_id):
    store = _store()
    season = os.getenv('FPL_SEASON', 'current')
    try:
        gameweek = FPLAPIClient.get_current_gameweek()
        tracked = store.import_team(team_id, season, FPLAPIClient.get_team_data(team_id), gameweek,
                                    FPLAPIClient.get_team_picks(team_id, gameweek), FPLAPIClient.get_team_history(team_id))
        return jsonify({'team': tracked, 'current_gameweek': gameweek}), 200
    except Exception as error:
        store.mark_refresh_failed(team_id, season, str(error))
        return api_error_response(error)
