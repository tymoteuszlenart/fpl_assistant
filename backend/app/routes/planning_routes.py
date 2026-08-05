"""Versioned Phase 2 projection and transfer-planning endpoints."""

from flask import current_app, jsonify, request

from app.routes import planning_bp
from app.routes.recommendation_routes import api_error_response
from app.services.projection_engine import build_baseline_projections
from app.services.tracked_team_store import TrackedTeamStore
from app.services.transfer_planner import plan_one_transfer
from app.services.squad_optimizer import optimize_squad
from app.services.strategy_service import squad_alerts, strategy_state
from app.utils.fpl_api import FPLAPIClient


def _store():
    return TrackedTeamStore(current_app.config['DATABASE'])


def _gameweeks(payload):
    gameweeks = payload.get('gameweeks')
    if not isinstance(gameweeks, list) or not gameweeks or any(not isinstance(gw, int) or gw < 1 for gw in gameweeks):
        raise ValueError('gameweeks must be a non-empty list of positive integers.')
    return list(dict.fromkeys(gameweeks))


@planning_bp.route('/projections/refresh', methods=['POST'])
def refresh_projections():
    try:
        gameweeks = _gameweeks(request.get_json(silent=True) or {})
        bootstrap, fixtures = FPLAPIClient.get_bootstrap_static(), FPLAPIClient.get_fixtures()
        projections, warnings = build_baseline_projections(bootstrap.get('elements', []), fixtures, gameweeks)
        projection_set = _store().save_projection_set('current', gameweeks, projections, warnings)
        return jsonify({'projection_set': projection_set, 'coverage': len(projections)}), 201
    except ValueError as error:
        return jsonify({'error': {'code': 'invalid_input', 'message': str(error), 'retryable': False}}), 400
    except Exception as error:
        return api_error_response(error)


@planning_bp.route('/projections/latest', methods=['GET'])
def latest_projections():
    projection_set = _store().latest_projection_set()
    if not projection_set:
        return jsonify({'error': {'code': 'not_found', 'message': 'No projection set has been generated.', 'retryable': False}}), 404
    return jsonify({'projection_set': projection_set}), 200


@planning_bp.route('/tracked-teams/<int:team_id>/strategy', methods=['GET'])
def get_strategy_state(team_id):
    used_chips = _store().used_chips(team_id)
    if used_chips is None:
        return jsonify({'error': {'code': 'not_found', 'message': 'Tracked team was not found.', 'retryable': False}}), 404
    return jsonify(strategy_state(used_chips)), 200


@planning_bp.route('/tracked-teams/<int:team_id>/alerts', methods=['GET'])
def get_strategy_alerts(team_id):
    try:
        state = _store().latest_squad_state(team_id)
        if state is None:
            return jsonify({'error': {'code': 'not_found', 'message': 'Tracked team was not found.', 'retryable': False}}), 404
        bootstrap = FPLAPIClient.get_bootstrap_static()
        return jsonify({'alerts': squad_alerts(state['team'], state['snapshot'], state['picks'], bootstrap.get('elements', []))}), 200
    except Exception as error:
        return api_error_response(error)


def _optimize(payload, budget_tenths):
    gameweeks = _gameweeks(payload)
    projection_set = _store().latest_projection_set()
    if not projection_set:
        return None, jsonify({'error': {'code': 'missing_projections', 'message': 'Generate a projection set before optimizing.', 'retryable': False}}), 400
    if any(gameweek not in projection_set['gameweeks'] for gameweek in gameweeks):
        return None, jsonify({'error': {'code': 'missing_projections', 'message': 'The latest projection set does not cover every requested gameweek.', 'retryable': False}}), 400
    bootstrap = FPLAPIClient.get_bootstrap_static()
    result = optimize_squad(bootstrap.get('elements', []), _store().projection_values(projection_set['id']), gameweeks,
                            budget_tenths, payload.get('locked_player_ids'), payload.get('excluded_player_ids'), payload.get('alternative_count', 0))
    return {'run': {'kind': payload.get('kind', 'squad_builder'), 'status': result['status'], 'projection_set_id': projection_set['id'],
                    'ruleset_id': '2026-v1', 'optimizer_version': 'optimizer-0.1'}, 'solutions': result['solutions'], 'warnings': result['warnings']}, None, None


@planning_bp.route('/optimizations/squad', methods=['POST'])
def build_initial_squad():
    try:
        payload = request.get_json(silent=True) or {}
        result, error, status = _optimize(payload, payload.get('budget_tenths'))
        return (error, status) if error else (jsonify(result), 200 if result['run']['status'] == 'feasible' else 400)
    except ValueError as error:
        return jsonify({'error': {'code': 'invalid_input', 'message': str(error), 'retryable': False}}), 400
    except Exception as error:
        return api_error_response(error)


@planning_bp.route('/tracked-teams/<int:team_id>/optimizations/wildcard', methods=['POST'])
def build_wildcard_squad(team_id):
    try:
        payload, state = request.get_json(silent=True) or {}, _store().latest_squad_state(team_id)
        if state is None:
            return jsonify({'error': {'code': 'not_found', 'message': 'Tracked team was not found.', 'retryable': False}}), 404
        if state['snapshot'] is None:
            return jsonify({'error': {'code': 'missing_team_state', 'message': 'No complete squad snapshot is available.', 'retryable': False}}), 400
        selling_total = sum(pick['selling_price_tenths'] for pick in state['picks'] if isinstance(pick['selling_price_tenths'], int))
        if len(state['picks']) != 15 or any(not isinstance(pick['selling_price_tenths'], int) for pick in state['picks']) or not isinstance(state['snapshot']['bank_tenths'], int):
            return jsonify({'error': {'code': 'missing_team_state', 'message': 'Wildcard mode requires bank and selling prices for every owned player.', 'retryable': False}}), 400
        payload['kind'] = 'wildcard'
        result, error, status = _optimize(payload, selling_total + state['snapshot']['bank_tenths'])
        return (error, status) if error else (jsonify(result), 200 if result['run']['status'] == 'feasible' else 400)
    except ValueError as error:
        return jsonify({'error': {'code': 'invalid_input', 'message': str(error), 'retryable': False}}), 400
    except Exception as error:
        return api_error_response(error)


@planning_bp.route('/tracked-teams/<int:team_id>/optimizations/transfers', methods=['POST'])
def plan_transfers(team_id):
    try:
        payload, state = request.get_json(silent=True) or {}, _store().latest_squad_state(team_id)
        if state is None:
            return jsonify({'error': {'code': 'not_found', 'message': 'Tracked team was not found.', 'retryable': False}}), 404
        if state['snapshot'] is None:
            return jsonify({'error': {'code': 'missing_team_state', 'message': 'No complete squad snapshot is available.', 'retryable': False}}), 400
        projection_set = _store().latest_projection_set()
        if not projection_set:
            return jsonify({'error': {'code': 'missing_projections', 'message': 'Generate a projection set before planning transfers.', 'retryable': False}}), 400
        gameweeks = _gameweeks(payload)
        if payload.get('max_transfers', 1) != 1:
            return jsonify({'error': {'code': 'invalid_input', 'message': 'The initial planner supports exactly one transfer.', 'retryable': False}}), 400
        if any(gameweek not in projection_set['gameweeks'] for gameweek in gameweeks):
            return jsonify({'error': {'code': 'missing_projections', 'message': 'The latest projection set does not cover every requested gameweek.', 'retryable': False}}), 400
        bootstrap = FPLAPIClient.get_bootstrap_static()
        result = plan_one_transfer(state['snapshot'], state['picks'], bootstrap.get('elements', []),
                                   _store().projection_values(projection_set['id']), gameweeks, payload.get('overrides'))
        if result['status'] == 'invalid_input':
            return jsonify({'error': {'code': 'invalid_input', 'message': result['warnings'][0], 'retryable': False}}), 400
        minimum = payload.get('minimum_net_gain', 0)
        solutions = [solution for solution in result['solutions'] if solution['net_gain'] >= minimum]
        for index, solution in enumerate(solutions, 1):
            solution['rank'] = index
            solution['is_recommended'] = solution['net_gain'] > minimum
            solution['risk_adjustment'] = 0
            solution['terminal_adjustment'] = 0
            solution['validation_status'] = 'valid'
        return jsonify({'run': {'kind': 'transfer_plan', 'status': result['status'], 'snapshot_id': state['snapshot']['id'],
                                'projection_set_id': projection_set['id'], 'ruleset_id': '2026-v1', 'optimizer_version': 'optimizer-0.1'},
                        'baseline': result['baseline'], 'solutions': solutions, 'warnings': result['warnings']}), 200
    except ValueError as error:
        return jsonify({'error': {'code': 'invalid_input', 'message': str(error), 'retryable': False}}), 400
    except Exception as error:
        return api_error_response(error)
