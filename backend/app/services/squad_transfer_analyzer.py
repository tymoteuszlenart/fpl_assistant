"""Service for suggesting squad transfers based on current squad analysis"""
from typing import Dict, List, Tuple, Optional
from app.utils.fpl_api import FPLAPIClient
from app.services.team_analyzer import TeamAnalyzer
from app.services.recommendation_engine import RecommendationEngine

class SquadTransferAnalyzer:
    """Analyzes current squad and suggests specific player swaps"""
    
    def __init__(self, team_id: int):
        self.team_id = team_id
        self.analyzer = TeamAnalyzer(team_id)
        self.engine = RecommendationEngine(team_id)
        self.bootstrap = self.analyzer.bootstrap
        self.current_squad = self.analyzer.get_current_squad()
        self.all_players = self.bootstrap['elements']
        
    def get_squad_overview(self) -> Dict:
        """Get detailed squad overview with performance metrics and photos"""
        squad_details = []
        
        for player in self.current_squad:
            player_info = self._get_player_full_data(player['player_id'])
            
            price = player['price']
            total_points = player_info.get('total_points', 0)
            points_per_million = (total_points / price) if price > 0 else 0
            
            # Get player photo URL from FPL API
            player_photo_url = self._get_player_photo_url(player_info.get('code'))
            
            squad_details.append({
                'player_id': player['player_id'],
                'name': player['name'],
                'position': player['position'],
                'team': player['team'],
                'price': price,
                'form': player['form'],
                'total_points': total_points,
                'minutes': player_info.get('minutes', 0),
                'goals': player_info.get('goals_scored', 0),
                'assists': player_info.get('assists', 0),
                'clean_sheets': player_info.get('clean_sheets', 0),
                'selected_by_percent': float(player_info.get('selected_by_percent', 0)),
                'status': player_info.get('status', 'a'),
                'is_captain': player.get('captain', False),
                'is_vice_captain': player.get('vice_captain', False),
                'points_per_million': round(points_per_million, 2),
                'performance_rating': self._rate_performance(player_info, price),
                'photo_url': player_photo_url,
            })
        
        return {
            'squad': squad_details,
            'total_spent': sum(p['price'] for p in squad_details),
            'bank': self.analyzer.team_data.get('last_deadline_bank', 0) / 10,
            'squad_form': sum(p['form'] for p in squad_details) / len(squad_details) if squad_details else 0,
        }
    
    def analyze_squad_for_transfers(self) -> Dict:
        """Analyze current squad and identify underperformers"""
        analysis = {
            'summary': self.analyzer.get_team_summary(),
            'current_squad': self.current_squad,
            'underperformers': self._identify_underperformers(),
            'smart_swaps': self._generate_smart_swaps(),
        }
        return analysis
    
    def _identify_underperformers(self) -> List[Dict]:
        """Identify players underperforming relative to their price, ordered by urgency"""
        underperformers = []
        
        for player in self.current_squad:
            player_id = player['player_id']
            full_player_data = self._get_player_full_data(player_id)
            
            if not full_player_data:
                continue
            
            # Calculate underperformance score
            form = float(full_player_data.get('form', 0))
            price = player['price']
            selected_percent = float(full_player_data.get('selected_by_percent', 0))
            minutes = full_player_data.get('minutes', 0)
            points_per_game = full_player_data.get('points_per_game', 0)
            team_id = full_player_data.get('team', 0)
            
            # Calculate player performance score (form, value, fixtures, minutes)
            upcoming_fdr = self.engine._calculate_upcoming_fdr(team_id or 0, weeks=3)
            
            player_score = (
                (form * 0.40) +  # Form weight
                ((6 - upcoming_fdr) / 5 * 0.30) +  # Fixtures
                (min(minutes / 90, 1.0) * 0.20) +  # Playing time
                ((100 - selected_percent) / 100 * 0.10)  # Contrarian bonus
            )
            
            # Calculate urgency score (how badly they need to be replaced)
            urgency = 0.0
            
            # Not playing = highest urgency
            if minutes < 90:
                urgency += (1 - (minutes / 90)) * 2.0
            
            # Poor form = high urgency
            if form < 3:
                urgency += (3 - form) * 1.0
            
            # Expensive with low form = high urgency  
            if price > 8 and form < 5:
                urgency += (5 - form) * 0.5
            
            if urgency > 0.5:  # Only include real underperformers
                underperformers.append({
                    'player_id': player_id,
                    'name': player['name'],
                    'position': player['position'],
                    'team': player['team'],
                    'price': price,
                    'form': form,
                    'minutes': minutes,
                    'selected_by_percent': selected_percent,
                    'code': full_player_data.get('code'),
                    'player_score': round(player_score, 2),
                    'urgency': round(urgency, 2),
                    'reason': self._generate_underperformance_reason(
                        form, price, minutes, points_per_game, selected_percent
                    )
                })
        
        # Sort by urgency (most urgent first)
        return sorted(underperformers, key=lambda x: x['urgency'], reverse=True)
    
    
    def _generate_smart_swaps(self) -> Dict[str, List[Dict]]:
        """Generate specific 'swap out -> swap in' recommendations per position, ordered by urgency"""
        swaps_by_position = {
            'GK': [],
            'DEF': [],
            'MID': [],
            'FWD': []
        }
        
        underperformers = self._identify_underperformers()
        current_player_ids = {p['player_id'] for p in self.current_squad}
        
        for underperformer in underperformers:
            position = underperformer['position']
            
            # Max 5 swaps per position
            if len(swaps_by_position[position]) >= 5:
                continue
            
            swap_price = underperformer['price'] + self.analyzer.team_data.get('last_deadline_bank', 0) / 10
            
            # Find best replacements at same or lower price
            # Pass the underperformer's score so replacements can calculate improvement
            replacements = self._find_replacements(
                position, 
                swap_price,
                exclude_ids=current_player_ids,
                underperformer_score=underperformer['player_score'],
                limit=5
            )
            
            if replacements:
                swap_in_options = []
                for replacement in replacements[:5]:  # Top 5 alternatives
                    replacement_data = self._get_player_full_data(replacement['player_id'])
                    swap_in_options.append({
                        'player_id': replacement['player_id'],
                        'name': replacement['name'],
                        'team': replacement['team'],
                        'position': replacement['position'],
                        'price': replacement['price'],
                        'form': replacement['form'],
                        'reason': f"Form {replacement['form']} | Improvement +{replacement.get('improvement_vs_current', 0):.1f}",
                        'photo_url': self._get_player_photo_url(replacement_data.get('code')),
                    })
                
                swaps_by_position[position].append({
                    'swap_out': {
                        'name': underperformer['name'],
                        'price': underperformer['price'],
                        'reason': underperformer['reason'],
                        'photo_url': self._get_player_photo_url(underperformer['code']),
                    },
                    'swap_in_options': swap_in_options,
                })
        
        return swaps_by_position
    
    def _get_player_photo_url(self, player_code: Optional[int]) -> str:
        """Get player photo URL from our API proxy endpoint"""
        if not player_code:
            return "http://localhost:5000/api/photos/0.png"
        return f"http://localhost:5000/api/photos/{player_code}.png"
    
    def _find_replacements(
        self, 
        position: str, 
        max_price: float, 
        exclude_ids: set,
        underperformer_score: float = 0.0,
        limit: int = 5
    ) -> List[Dict]:
        """Find replacement players at a position within price range"""
        candidates = []
        
        for player in self.all_players:
            player_id = player['id']
            if player_id in exclude_ids:
                continue
            
            if self._get_position_name(player.get('element_type', 0)) != position:
                continue
            
            price = (player.get('now_cost', 0) or 0) / 10
            if price > max_price:
                continue
            
            if player.get('status') != 'a':  # Active only
                continue
            
            # Score this replacement
            form = float(player.get('form', 0))
            selected_percent = float(player.get('selected_by_percent', 0))
            minutes = player.get('minutes', 0)
            team_id = player.get('team', 0)
            
            upcoming_fdr = self.engine._calculate_upcoming_fdr(team_id or 0, weeks=3)
            
            # Replacement score: form + fixtures - high ownership
            replacement_score = (
                (form * 0.40) +
                ((6 - upcoming_fdr) / 5 * 0.30) +
                ((100 - selected_percent) / 100 * 0.20) +
                (min(minutes / 90, 1.0) * 0.10)
            )
            
            # Calculate improvement over current player
            improvement = replacement_score - underperformer_score
            
            candidates.append({
                'player_id': player_id,
                'name': player.get('web_name'),
                'team': self._get_team_name(team_id),
                'position': position,
                'price': price,
                'form': form,
                'minutes': minutes,
                'selected_by_percent': selected_percent,
                'upcoming_fdr': upcoming_fdr,
                'replacement_score': round(replacement_score, 2),
                'improvement_vs_current': round(improvement, 2),
                'price_diff': round(price - (max_price - self.analyzer.team_data.get('last_deadline_bank', 0) / 10), 2),
            })
        
        # Sort by improvement over current player (best improvement first)
        candidates.sort(key=lambda x: x['improvement_vs_current'], reverse=True)
        return candidates[:limit]
    
    def _get_player_full_data(self, player_id: int) -> Dict:
        """Get full player data from bootstrap"""
        for player in self.all_players:
            if player['id'] == player_id:
                return player
        return {}
    
    def _generate_underperformance_reason(
        self, 
        form: float, 
        price: float, 
        minutes: int, 
        ppg: float,
        selected: float
    ) -> str:
        """Generate human-readable reason for underperformance"""
        reasons = []
        
        if minutes == 0:
            reasons.append("Not playing")
        elif minutes < 90:
            reasons.append(f"Limited mins ({minutes})")
        
        if form < 3:
            reasons.append(f"Poor form ({form})")
        elif form < 5:
            reasons.append(f"Okay form ({form})")
        
        if price > 8:
            reasons.append(f"Expensive (£{price}m)")
        
        if selected > 30:
            reasons.append(f"High ownership ({selected:.0f}%)")
        
        if reasons:
            return " | ".join(reasons)
        return "Worth considering transfer"
    
    def _get_position_name(self, position_id: int) -> str:
        """Convert position ID to name"""
        positions = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
        return positions.get(position_id, 'Unknown')
    
    def _get_team_name(self, team_id: int) -> str:
        """Get team name from ID"""
        if not team_id:
            return 'Unknown'
        for team in self.bootstrap['teams']:
            if team['id'] == team_id:
                return team['short_name']
        return 'Unknown'
    
    def _rate_performance(self, player_info: Dict, price: float) -> str:
        """Rate player performance as Excellent, Good, Average, Poor"""
        total_points = player_info.get('total_points', 0)
        points_per_million = (total_points / price) if price > 0 else 0
        form = float(player_info.get('form', 0))
        
        # Combined score
        score = (form * 0.4) + (points_per_million * 0.6)
        
        if score > 6:
            return "Excellent"
        elif score > 4:
            return "Good"
        elif score > 2:
            return "Average"
        else:
            return "Poor"
