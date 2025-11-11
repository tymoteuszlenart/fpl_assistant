import requests
import os
from typing import Dict, List, Optional
from functools import lru_cache
import json

FPL_API_BASE = os.getenv('FPL_API_BASE_URL', 'https://fantasy.premierleague.com/api')

# Headers to avoid 403 Forbidden from FPL API
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

class FPLAPIClient:
    """Client for interacting with FPL API"""
    
    @staticmethod
    @lru_cache(maxsize=128)
    def get_bootstrap_static() -> Dict:
        """Fetch static bootstrap data (teams, players, positions, etc.)"""
        try:
            response = requests.get(f"{FPL_API_BASE}/bootstrap-static/", headers=HEADERS)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch bootstrap data: {str(e)}")
    
    @staticmethod
    def get_current_gameweek() -> int:
        """Dynamically fetch current gameweek"""
        try:
            bootstrap = FPLAPIClient.get_bootstrap_static()
            current_gw = bootstrap['events'][0]['id']
            for event in bootstrap['events']:
                if event['is_current']:
                    current_gw = event['id']
                    break
            return current_gw
        except Exception as e:
            raise Exception(f"Failed to fetch current gameweek: {str(e)}")
    
    @staticmethod
    def get_team_data(team_id: int) -> Dict:
        """Fetch team data by team ID"""
        try:
            response = requests.get(f"{FPL_API_BASE}/entry/{team_id}/", headers=HEADERS)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch team {team_id}: {str(e)}")
    
    @staticmethod
    def get_team_picks(team_id: int, gameweek: int) -> List[Dict]:
        """Fetch team picks for a specific gameweek"""
        try:
            response = requests.get(f"{FPL_API_BASE}/entry/{team_id}/event/{gameweek}/picks/", headers=HEADERS)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch team picks for GW{gameweek}: {str(e)}")
    
    @staticmethod
    def get_player_data(player_id: int) -> Dict:
        """Fetch detailed player data"""
        try:
            response = requests.get(f"{FPL_API_BASE}/element/{player_id}/", headers=HEADERS)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch player {player_id}: {str(e)}")
    
    @staticmethod
    def get_fixtures() -> List[Dict]:
        """Fetch all fixtures"""
        try:
            response = requests.get(f"{FPL_API_BASE}/fixtures/", headers=HEADERS)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch fixtures: {str(e)}")
    
    @staticmethod
    def get_team_fixtures(team_id: int) -> List[Dict]:
        """Fetch fixtures for a specific team"""
        try:
            response = requests.get(f"{FPL_API_BASE}/fixtures/?team={team_id}", headers=HEADERS)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch fixtures for team {team_id}: {str(e)}")
