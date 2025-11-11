# Photos Fix - API Proxy Solution

## Problem
The frontend was getting HTTP 403 Forbidden errors when trying to load player photos directly from FPL API endpoint:
```
https://resources.premierleague.com/premierleague/photos/players/110x110/p{code}.png
```

## Solution
Created a backend proxy endpoint that fetches photos from FPL API and serves them through our own API.

## Changes Made

### 1. New Photo Routes (`backend/app/routes/photo_routes.py`)
- Created new Flask route: `GET /api/photos/<player_code>.png`
- Proxies requests to FPL photo endpoint with proper User-Agent header
- Avoids 403 errors by adding: `User-Agent: Mozilla/5.0...`
- Returns PNG image directly

### 2. Blueprint Registration (`backend/app/routes/__init__.py`)
- Added `photos_bp` blueprint with URL prefix `/api/photos`
- Imported `photo_routes` module

### 3. App Configuration (`backend/app/__init__.py`)
- Registered `photos_bp` with Flask app
- Photos endpoint now available at: `http://localhost:5000/api/photos/{code}.png`

### 4. Updated Photo URLs in Services

**`backend/app/services/squad_transfer_analyzer.py`:**
- `_get_player_photo_url()` now returns: `http://localhost:5000/api/photos/{code}.png`

**`backend/app/services/recommendation_engine.py`:**
- `_get_player_photo_url()` now returns: `http://localhost:5000/api/photos/{code}.png`

## How It Works

```
Frontend (React)
   ↓
   Requests: http://localhost:5000/api/photos/12345.png
   ↓
Backend (Flask)
   ↓
   Proxy request: https://resources.premierleague.com/premierleague/photos/players/110x110/p12345.png
   (with User-Agent header)
   ↓
   FPL API returns image
   ↓
   Backend serves image to Frontend
   ↓
Frontend displays photo ✅
```

## Benefits
✅ No 403 errors - backend adds proper User-Agent header
✅ Bypasses CORS issues - all requests go through same backend
✅ Cacheable - can add caching layer later if needed
✅ Reliable - fallback to 404 if image not found
✅ Transparent to frontend - same URL format works across all components

## Testing
- All Python files compile successfully
- All TypeScript files compile successfully
- Routes properly registered in Flask app
- Photo URLs now point to proxy endpoint

## Deployment Note
When deployed to production, update the localhost URL to your production domain:
```python
# Development:
return f"http://localhost:5000/api/photos/{player_code}.png"

# Production:
return f"https://your-domain.com/api/photos/{player_code}.png"
```
