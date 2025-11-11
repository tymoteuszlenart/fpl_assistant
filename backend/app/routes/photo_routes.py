"""Routes for serving player photos from FPL API"""
from flask import Response, make_response
import requests
from . import photos_bp

@photos_bp.route('/<int:player_code>.png', methods=['GET', 'OPTIONS'])
def get_player_photo(player_code):
    """Proxy player photo from FPL API"""
    try:
        url = f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{player_code}.png"
        
        # Use User-Agent header to avoid 403
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        flask_response = make_response(response.content)
        return flask_response
    except requests.RequestException as e:
        # Return 404 on error
        error_response = make_response(b'', 404)
        return error_response

