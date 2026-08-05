"""Routes for serving player photos from FPL API"""
from flask import Response, make_response
import requests
from . import photos_bp

# Simple SVG placeholder as bytes
def get_placeholder_svg():
    """Generate a simple SVG placeholder image"""
    svg = b'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="110" height="140" viewBox="0 0 110 140" xmlns="http://www.w3.org/2000/svg">
  <rect width="110" height="140" fill="#e8e8e8"/>
  <circle cx="55" cy="45" r="20" fill="#999"/>
  <path d="M 20 120 Q 55 95 90 120 L 90 140 L 20 140 Z" fill="#999"/>
</svg>'''
    return svg

@photos_bp.route('/<int:player_code>.png', methods=['GET', 'OPTIONS'])
def get_player_photo(player_code):
    """Proxy player photo from FPL API with fallback to placeholder"""    
    
    try:
        url = f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{player_code}.png"
        
        # Use User-Agent header to avoid 403
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Return placeholder for response code 404 (no player)
        if response.status_code == 404:
            return serve_placeholder()

        flask_response = make_response(response.content)
        flask_response.headers['Content-Type'] = 'image/png'
        flask_response.headers['Cache-Control'] = 'public, max-age=86400'
        return flask_response
    except requests.RequestException as e:
        # Return placeholder on any error
        return serve_placeholder()


def serve_placeholder():
    """Serve a placeholder SVG when photo is not available"""
    response = make_response(get_placeholder_svg())
    response.headers['Content-Type'] = 'image/svg+xml'
    response.headers['Cache-Control'] = 'public, max-age=3600'
    return response



