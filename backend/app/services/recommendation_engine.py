"""Service for generating transfer recommendations"""
from typing import Dict, List, Optional
from app.utils.fpl_api import FPLAPIClient
from app.services.team_analyzer import TeamAnalyzer
from collections import defaultdict

class RecommendationEngine:
    """Generates optimized transfer recommendations"""
    
    def __init__(self, team_id: int):
        self.team_id = team_id
        self.analyzer = TeamAnalyzer(team_id)
        self.bootstrap = self.analyzer.bootstrap
        self.current_gameweek = self.analyzer.current_gameweek
        self.all_players = self.bootstrap['elements']
        self.fixtures = self.analyzer.fixtures
        
    def get_best_transfers_per_position(self) -> Dict[str, List[Dict]]:
        """Get best 5 transfer options per position"""
        current_squad = self.analyzer.get_current_squad()
        current_player_ids = {p['player_id'] for p in current_squad}
        
        recommendations = {}
        
        for position in ['GK', 'DEF', 'MID', 'FWD']:
            # Get players in squad for this position
            squad_players = [p for p in current_squad if p['position'] == position]
            
            # Get available players for this position (not in squad)
            available_players = [
                p for p in self.all_players 
                if self._get_position_name(p.get('element_type', 0)) == position
                and p['id'] not in current_player_ids
                and p.get('status') == 'a'  # Active only
            ]
            
            # Score and rank players
            scored_players = [
                self._score_player_for_transfer(p, position)
                for p in available_players
            ]
            
            # Get top 5
            top_5 = sorted(scored_players, key=lambda x: x['score'], reverse=True)[:5]
            recommendations[position] = top_5
        
        return recommendations
    
    def get_high_upside_differentials(self, count: int = 5) -> Dict[str, List[Dict]]:
        """Get high-upside differentials organized by position (5 per position)"""
        current_squad = self.analyzer.get_current_squad()
        current_player_ids = {p['player_id'] for p in current_squad}
        
        # Get available players
        available_players = [
            p for p in self.all_players
            if p['id'] not in current_player_ids
            and p.get('status') == 'a'
        ]
        
        # Score differentials
        differential_scores = [
            self._score_differential(p)
            for p in available_players
        ]
        
        # Group by position and get top 5 per position
        by_position = defaultdict(list)
        for diff in differential_scores:
            by_position[diff['position']].append(diff)
        
        # Get top 5 per position
        result = {}
        for position in ['GK', 'DEF', 'MID', 'FWD']:
            top_differentials = sorted(
                by_position.get(position, []), 
                key=lambda x: x['differential_score'], 
                reverse=True
            )[:count]
            result[position] = top_differentials
        
        return result
    
    def _score_player_for_transfer(self, player: Dict, position: str) -> Dict:
        """Score a player for transfer recommendation"""
        player_id = player['id']
        
        # Base metrics
        form = float(player.get('form', 0))
        now_cost = (player.get('now_cost', 0) or 0) / 10
        selected_percent = float(player.get('selected_by_percent', 0))
        minutes = player.get('minutes', 0)
        
        # Calculate expected points based on recent form and cost
        expected_points_this_week = self._calculate_expected_points(player)
        
        # Get upcoming fixture difficulty
        team_id: int = player.get('team', 0) or 0
        upcoming_fdr = self._calculate_upcoming_fdr(team_id, weeks=3)
        
        # Get player photo
        player_code = player.get('code')
        photo_url = self._get_player_photo_url(player_code)
        
        # Value score: form relative to cost
        value_score = (form / now_cost) if now_cost > 0 else 0
        
        # Consistency score: inverse of ownership (contrarian edge)
        ownership_score = (100 - selected_percent) / 100
        
        # Fixture score: better if facing weaker opponents
        fixture_score = (6 - upcoming_fdr) / 5  # FDR is 1-5, invert it
        
        # Playing time score
        playing_time_score = min(minutes / 90, 1.0)  # Normalize to 1.0
        
        # Composite score
        composite_score = (
            (form * 0.25) +  # Form weight
            (value_score * 0.20) +  # Value weight
            (ownership_score * 0.15) +  # Contrarian weight
            (fixture_score * 0.25) +  # Fixture difficulty weight
            (playing_time_score * 0.15)  # Playing time weight
        )
        
        return {
            'player_id': player_id,
            'name': player.get('web_name'),
            'team': self._get_team_name(team_id),
            'position': position,
            'price': now_cost,
            'form': form,
            'selected_by_percent': selected_percent,
            'minutes': minutes,
            'expected_points_this_week': round(expected_points_this_week, 2),
            'upcoming_fdr': upcoming_fdr,
            'value_score': round(value_score, 2),
            'ownership_score': round(ownership_score, 2),
            'fixture_score': round(fixture_score, 2),
            'playing_time_score': round(playing_time_score, 2),
            'score': round(composite_score, 2),
            'reason': self._generate_recommendation_reason(player, form, ownership_score, upcoming_fdr),
            'photo_url': photo_url,
        }
    
    def _score_differential(self, player: Dict) -> Dict:
        """Score a player as a potential differential"""
        player_id = player['id']
        
        form = float(player.get('form', 0))
        selected_percent = float(player.get('selected_by_percent', 0))
        minutes = player.get('minutes', 0)
        team_id: int = player.get('team', 0) or 0
        now_cost = (player.get('now_cost', 0) or 0) / 10
        
        # Expected points
        expected_points = self._calculate_expected_points(player)
        
        # Upside: low ownership + good form + good fixtures
        ownership_factor = (100 - selected_percent) / 100  # Low ownership is good
        form_factor = max(0, form)  # Recent form
        upcoming_fdr = self._calculate_upcoming_fdr(team_id, weeks=3)
        fixture_factor = (6 - upcoming_fdr) / 5
        
        # Differential score
        differential_score = (
            (form_factor * 0.30) +
            (ownership_factor * 0.40) +  # Ownership is key for differentials
            (fixture_factor * 0.20) +
            (minutes / 90 * 0.10)  # Playing time bonus
        )
        
        position = self._get_position_name(player.get('element_type', 0))
        player_code = player.get('code')
        photo_url = self._get_player_photo_url(player_code)
        
        return {
            'player_id': player_id,
            'name': player.get('web_name'),
            'team': self._get_team_name(team_id),
            'position': position,
            'price': now_cost,
            'form': form,
            'selected_by_percent': selected_percent,
            'ownership_rank': round(selected_percent, 1),
            'expected_points': round(expected_points, 2),
            'upcoming_fdr': upcoming_fdr,
            'differential_score': round(differential_score, 2),
            'reason': f"Low ownership ({selected_percent:.1f}%) with form {form} and facing FDR {upcoming_fdr:.1f}",
            'photo_url': photo_url,
        }
    
    def _calculate_expected_points(self, player: Dict) -> float:
        """Estimate expected points based on recent form and position"""
        form = float(player.get('form', 0))
        position = self._get_position_name(player.get('element_type', 0))
        
        # Position multipliers (forwards score more points per goal)
        position_multipliers = {
            'GK': 1.2,
            'DEF': 1.5,
            'MID': 2.0,
            'FWD': 2.5
        }
        
        multiplier = position_multipliers.get(position, 1.0)
        expected = form * multiplier
        
        return expected
    
    def _calculate_upcoming_fdr(self, team_id: int, weeks: int = 3) -> float:
        """Calculate average fixture difficulty rating for upcoming weeks"""
        if not team_id:
            return 3.0  # Default medium difficulty
        
        upcoming_fdr_values = []
        fixture_count = 0
        
        for fixture in self.fixtures:
            event = fixture.get('event', 0) or 0
            if event >= self.current_gameweek and fixture_count < weeks:
                if fixture['team_a'] == team_id:
                    fdr = fixture.get('team_a_difficulty', 3)
                    upcoming_fdr_values.append(fdr)
                    fixture_count += 1
                elif fixture['team_h'] == team_id:
                    fdr = fixture.get('team_h_difficulty', 3)
                    upcoming_fdr_values.append(fdr)
                    fixture_count += 1
        
        return sum(upcoming_fdr_values) / len(upcoming_fdr_values) if upcoming_fdr_values else 3.0
    
    def _generate_recommendation_reason(self, player: Dict, form: float, ownership: float, fdr: float) -> str:
        """Generate human-readable reason for recommendation"""
        reasons = []
        
        if form > 5:
            reasons.append(f"Excellent form ({form})")
        elif form > 3:
            reasons.append(f"Good form ({form})")
        
        if ownership < 0.1:
            reasons.append("Very low ownership")
        elif ownership < 0.3:
            reasons.append("Low ownership")
        
        if fdr < 3:
            reasons.append(f"Easy fixtures ahead (FDR {fdr:.1f})")
        
        if not reasons:
            reasons.append("Solid potential")
        
        return " | ".join(reasons)
    
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
    
    def _get_player_photo_url(self, player_code: Optional[int]) -> str:
        """Get player photo URL from our API proxy endpoint"""
        if not player_code:
            return "http://localhost:5000/api/photos/0.png"
        return f"http://localhost:5000/api/photos/{player_code}.png"
    
    def get_smart_recommendations(self) -> Dict:
        """Get all recommendations in one call"""
        return {
            'current_gameweek': self.current_gameweek,
            'best_transfers_per_position': self.get_best_transfers_per_position(),
            'high_upside_differentials': self.get_high_upside_differentials(),
        }
