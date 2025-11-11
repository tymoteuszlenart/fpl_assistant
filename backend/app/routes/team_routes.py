from flask import request, jsonify
from . import team_bp
from app.services.team_analyzer import TeamAnalyzer
from app.services.squad_transfer_analyzer import SquadTransferAnalyzer
from app.utils.fpl_api import FPLAPIClient

@team_bp.route('/current-gameweek', methods=['GET'])
def get_current_gameweek():
    """Get current gameweek"""
    try:
        gameweek = FPLAPIClient.get_current_gameweek()
        return jsonify({'current_gameweek': gameweek}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@team_bp.route('/<int:team_id>/summary', methods=['GET'])
def get_team_summary(team_id):
    """Get team summary"""
    try:
        analyzer = TeamAnalyzer(team_id)
        summary = analyzer.get_team_summary()
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@team_bp.route('/<int:team_id>/squad', methods=['GET'])
def get_team_squad(team_id):
    """Get current squad"""
    try:
        analyzer = TeamAnalyzer(team_id)
        squad = analyzer.get_current_squad()
        return jsonify({'squad': squad}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@team_bp.route('/<int:team_id>/analysis', methods=['GET'])
def get_team_analysis(team_id):
    """Get detailed team analysis"""
    try:
        analyzer = TeamAnalyzer(team_id)
        analysis = analyzer.analyze_squad_health()
        return jsonify(analysis), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@team_bp.route('/<int:team_id>/detailed-analysis', methods=['GET'])
def get_detailed_team_analysis(team_id):
    """Get comprehensive team analysis including depth and upcoming fixtures"""
    try:
        analyzer = TeamAnalyzer(team_id)
        analysis = analyzer.get_detailed_analysis()
        return jsonify(analysis), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@team_bp.route('/<int:team_id>/depth', methods=['GET'])
def get_squad_depth(team_id):
    """Get squad depth analysis"""
    try:
        analyzer = TeamAnalyzer(team_id)
        depth = analyzer.analyze_squad_depth()
        return jsonify(depth), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@team_bp.route('/<int:team_id>/transfer-analysis', methods=['GET'])
def get_squad_transfer_analysis(team_id):
    """Get squad transfer analysis with smart swaps"""
    try:
        analyzer = SquadTransferAnalyzer(team_id)
        analysis = analyzer.analyze_squad_for_transfers()
        return jsonify(analysis), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@team_bp.route('/<int:team_id>/underperformers', methods=['GET'])
def get_underperformers(team_id):
    """Get list of underperforming players in current squad"""
    try:
        analyzer = SquadTransferAnalyzer(team_id)
        underperformers = analyzer._identify_underperformers()
        return jsonify({'underperformers': underperformers}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@team_bp.route('/<int:team_id>/smart-swaps', methods=['GET'])
def get_smart_swaps(team_id):
    """Get smart swap recommendations for each position"""
    try:
        analyzer = SquadTransferAnalyzer(team_id)
        swaps = analyzer._generate_smart_swaps()
        return jsonify({'smart_swaps': swaps}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@team_bp.route('/<int:team_id>/squad-overview', methods=['GET'])
def get_squad_overview(team_id):
    """Get detailed squad overview with performance metrics"""
    try:
        analyzer = SquadTransferAnalyzer(team_id)
        overview = analyzer.get_squad_overview()
        return jsonify(overview), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
