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


class FPLAPIError(Exception):
    """The official FPL API could not serve a usable response."""


class FPLResourceNotFound(FPLAPIError):
    """A public FPL resource (such as a team) does not exist."""


def _get_json(path: str) -> Dict:
    """Fetch one official payload with a bounded request time."""
    try:
        response = requests.get(
            f"{FPL_API_BASE}{path}", headers=HEADERS, timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as error:
        if error.response is not None and error.response.status_code == 404:
            raise FPLResourceNotFound("The requested FPL resource was not found.") from error
        raise FPLAPIError("The official FPL API returned an error.") from error
    except (requests.RequestException, ValueError) as error:
        raise FPLAPIError("The official FPL API is temporarily unavailable.") from error

class FPLAPIClient:
    """Client for interacting with FPL API"""
    
    @staticmethod
    @lru_cache(maxsize=128)
    def get_bootstrap_static() -> Dict:
        """Fetch static bootstrap data (teams, players, positions, etc.)"""
        return _get_json("/bootstrap-static/")
    
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
        return _get_json(f"/entry/{team_id}/")
    
    @staticmethod
    def get_team_picks(team_id: int, gameweek: int) -> Dict:
        """Fetch team picks for a specific gameweek"""
        return _get_json(f"/entry/{team_id}/event/{gameweek}/picks/")
    
    @staticmethod
    def get_player_data(player_id: int) -> Dict:
        """Fetch detailed player data"""
        return _get_json(f"/element/{player_id}/")
    
    @staticmethod
    def get_fixtures() -> List[Dict]:
        """Fetch all fixtures"""
        return _get_json("/fixtures/")
    
    @staticmethod
    def get_team_fixtures(team_id: int) -> List[Dict]:
        """Fetch fixtures for a specific team"""
        return _get_json(f"/fixtures/?team={team_id}")
