# CORS Configuration - Cross-Origin Resource Sharing

## Problem
Frontend running on `http://localhost:3000` needs to access:
- API endpoints on `http://localhost:5000/api/*`
- Images served by proxy on `http://localhost:5000/api/photos/*`

Without proper CORS headers, browsers block these requests with errors.

## Solution

### Backend Configuration (`app/__init__.py`)

```python
cors_config = {
    "origins": ["http://localhost:3000", "http://localhost:5000"],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"],
    "supports_credentials": True
}
CORS(app, resources={r"/api/*": cors_config})
```

### Photo Endpoint CORS Headers (`app/routes/photo_routes.py`)

Every response includes:
```python
flask_response.headers['Access-Control-Allow-Origin'] = '*'
flask_response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
flask_response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
```

## How CORS Works

1. **Browser makes request from localhost:3000**
   ```
   GET http://localhost:5000/api/photos/12345.png
   Origin: http://localhost:3000
   ```

2. **Backend checks CORS configuration**
   - Is the origin in the allowed list?
   - Is the method allowed?
   - Are the headers allowed?

3. **Backend responds with CORS headers**
   ```
   Access-Control-Allow-Origin: http://localhost:3000
   Access-Control-Allow-Methods: GET, POST, etc.
   Content-Type: image/png
   ```

4. **Browser receives response**
   - CORS headers match? ✅ Allow access
   - Image displays on page

## Headers Explained

| Header | Purpose |
|--------|---------|
| `Access-Control-Allow-Origin` | Which domains can access this resource |
| `Access-Control-Allow-Methods` | Which HTTP methods are allowed (GET, POST, etc.) |
| `Access-Control-Allow-Headers` | Which request headers are allowed |
| `Access-Control-Allow-Credentials` | Whether cookies can be sent |

## For Development
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:5000`
- Both included in allowed origins ✅

## For Production
Update `app/__init__.py` to use production domains:

```python
cors_config = {
    "origins": ["https://your-domain.com", "https://api.your-domain.com"],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"],
    "supports_credentials": True
}
```

## Troubleshooting

### Still getting CORS errors?
1. Check browser console for exact error message
2. Verify frontend and backend are on correct ports
3. Check that backend is running with correct CORS config
4. Reload browser (hard refresh: Cmd+Shift+R / Ctrl+Shift+R)

### Images still not loading?
1. Check Network tab in DevTools
2. Verify `Access-Control-Allow-Origin` header is present
3. Check HTTP status code (should be 200, not 403 or 404)
4. Verify player code is valid and exists in FPL API
