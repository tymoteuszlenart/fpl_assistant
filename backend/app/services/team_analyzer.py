"""Service for analyzing FPL teams"""
from typing import Dict, List, Optional, Tuple
from app.utils.fpl_api import FPLAPIClient
import json
from datetime import datetime, timedelta

class TeamAnalyzer:
    """Analyzes FPL team data"""
    
    def __init__(self, team_id: int):
        self.team_id = team_id
        self.current_gameweek = FPLAPIClient.get_current_gameweek()
        self.bootstrap = FPLAPIClient.get_bootstrap_static()
        self.team_data = FPLAPIClient.get_team_data(team_id)
        self.team_picks = FPLAPIClient.get_team_picks(team_id, self.current_gameweek)
        self.fixtures = FPLAPIClient.get_fixtures()
        
    def get_team_summary(self) -> Dict:
        """Get team summary information"""
        first_name = self.team_data.get('player_first_name', '')
        last_name = self.team_data.get('player_last_name', '')
        bank = self.team_data.get('last_deadline_bank', 0)
        
        return {
            'team_id': self.team_id,
            'team_name': self.team_data.get('name'),
            'manager_name': f"{first_name} {last_name}".strip(),
            'current_rank': self.team_data.get('summary_overall_rank'),
            'total_points': self.team_data.get('summary_overall_points'),
            'current_gameweek': self.current_gameweek,
            'transfers_remaining': self.team_data.get('transfers_available'),
            'transfer_bank': bank / 10 if bank else 0,  # Convert from 1/10ths
        }
    
    def get_current_squad(self) -> List[Dict]:
        """Get current squad with detailed player information"""
        squad = []
        
        # Handle both dict and list responses from API
        picks = self.team_picks.get('picks', []) if isinstance(self.team_picks, dict) else self.team_picks
        
        for pick in picks:
            player_id = pick['element']
            player = self._get_player_info(player_id)
            
            position_id: int = player.get('element_type', 0) or 0
            team_id: int = player.get('team', 0) or 0
            cost: int = player.get('now_cost', 0) or 0
            
            squad.append({
                'player_id': player_id,
                'name': player.get('web_name'),
                'position': self._get_position_name(position_id),
                'team': self._get_team_name(team_id),
                'price': cost / 10,  # Convert from 1/10ths
                'form': float(player.get('form', 0)),
                'selected': pick.get('multiplier'),
                'captain': pick.get('is_captain'),
                'vice_captain': pick.get('is_vice_captain'),
            })
        
        return squad
    
    def _get_player_info(self, player_id: int) -> Dict:
        """Get player information from bootstrap data"""
        for player in self.bootstrap['elements']:
            if player['id'] == player_id:
                return player
        return {}
    
    def _get_position_name(self, position_id: int) -> str:
        """Convert position ID to name"""
        positions = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
        return positions.get(position_id, 'Unknown')
    
    def _get_team_name(self, team_id: int) -> str:
        """Get team name from ID"""
        for team in self.bootstrap['teams']:
            if team['id'] == team_id:
                return team['short_name']
        return 'Unknown'
    
    def analyze_squad_health(self) -> Dict:
        """Analyze squad form, fixtures, and potential issues"""
        squad = self.get_current_squad()
        
        analysis = {
            'total_squad_form': sum(p['form'] for p in squad) / len(squad) if squad else 0,
            'players_by_position': {},
            'upcoming_fixtures': self._get_upcoming_fixtures(),
        }
        
        # Group players by position
        for position in ['GK', 'DEF', 'MID', 'FWD']:
            players = [p for p in squad if p['position'] == position]
            analysis['players_by_position'][position] = {
                'count': len(players),
                'avg_form': sum(p['form'] for p in players) / len(players) if players else 0,
                'avg_price': sum(p['price'] for p in players) / len(players) if players else 0,
                'players': players
            }
        
        return analysis
    
    def _get_upcoming_fixtures(self, gameweeks: int = 3) -> List[Dict]:
        """Get upcoming fixtures for the team"""
        team_id = self.team_data.get('favourite_team')
        
        upcoming = []
        for fixture in self.fixtures:
            if fixture['event'] and fixture['event'] >= self.current_gameweek:
                if fixture['team_a'] == team_id or fixture['team_h'] == team_id:
                    upcoming.append({
                        'gameweek': fixture['event'],
                        'opponent': self._get_team_name(fixture['team_h'] if fixture['team_a'] == team_id else fixture['team_a']),
                        'home': fixture['team_h'] == team_id,
                        'difficulty': fixture['team_a_difficulty'] if fixture['team_a'] == team_id else fixture['team_h_difficulty']
                    })
                    
            if len(upcoming) >= gameweeks:
                break
        
        return upcoming
    
    def get_player_performance_stats(self, player_id: int) -> Dict:
        """Get performance statistics for a player"""
        player = self._get_player_info(player_id)
        
        if not player:
            return {}
        
        return {
            'player_id': player_id,
            'name': player.get('web_name'),
            'team': self._get_team_name(player.get('team', 0) or 0),
            'position': self._get_position_name(player.get('element_type', 0) or 0),
            'form': float(player.get('form', 0)),
            'total_points': player.get('total_points', 0),
            'minutes': player.get('minutes', 0),
            'goals': player.get('goals_scored', 0),
            'assists': player.get('assists', 0),
            'clean_sheets': player.get('clean_sheets', 0),
            'now_cost': (player.get('now_cost', 0) or 0) / 10,
            'selected_by_percent': float(player.get('selected_by_percent', 0)),
            'status': player.get('status'),  # 'a' for active, 'i' for injured, 'u' for unavailable
        }
    
    def get_squad_by_position(self) -> Dict[str, List[Dict]]:
        """Group squad players by position"""
        squad = self.get_current_squad()
        grouped = {
            'GK': [],
            'DEF': [],
            'MID': [],
            'FWD': []
        }
        
        for player in squad:
            position = player['position']
            if position in grouped:
                grouped[position].append(player)
        
        return grouped
    
    def analyze_squad_depth(self) -> Dict:
        """Analyze squad depth and potential weaknesses"""
        squad_by_pos = self.get_squad_by_position()
        
        depth_analysis = {}
        for position, players in squad_by_pos.items():
            player_forms = [p['form'] for p in players]
            player_teams = [p['team'] for p in players]
            
            # Check for team duplication (high concentration risk)
            team_counts = {}
            for team in player_teams:
                team_counts[team] = team_counts.get(team, 0) + 1
            
            depth_analysis[position] = {
                'count': len(players),
                'avg_form': sum(player_forms) / len(player_forms) if player_forms else 0,
                'min_form': min(player_forms) if player_forms else 0,
                'max_form': max(player_forms) if player_forms else 0,
                'team_concentration': team_counts,
                'players': players
            }
        
        return depth_analysis
    
    def get_detailed_analysis(self) -> Dict:
        """Get comprehensive team analysis"""
        return {
            'summary': self.get_team_summary(),
            'squad': self.get_current_squad(),
            'health': self.analyze_squad_health(),
            'depth': self.analyze_squad_depth(),
            'upcoming_fixtures': self._get_upcoming_fixtures(gameweeks=5),
        }
