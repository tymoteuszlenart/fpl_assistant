# Debugging Transfers Not Showing

## Common Causes

### 1. **Empty Recommendations** (Most Common)
**Symptoms**: "No transfer recommendations available" message or blank positions

**Causes**:
- All available players already in squad
- No eligible players for some position
- Filtering issue (all players marked as inactive)

**How to check**:
- Look at `_debug` field in API response:
  ```
  "_debug": {
    "team_id": 12345,
    "positions_with_recommendations": {
      "GK": 0,
      "DEF": 5,
      "MID": 4,
      "FWD": 2
    }
  }
  ```
- If GK is 0, no eligible GK alternatives available

### 2. **API Request Error**
**Symptoms**: "Error" message in UI

**Causes**:
- Backend not running
- Team ID doesn't exist
- API connection issue

**How to check**:
```bash
# Test the endpoint directly
curl http://localhost:5000/api/recommendations/123456/transfers
```

### 3. **Frontend Not Receiving Data**
**Symptoms**: Loads forever or no error message

**Causes**:
- CORS issue
- Network error
- Malformed response

**How to check**:
- Open browser DevTools (F12)
- Go to Network tab
- Click "Best Transfers" tab
- Look for failed requests
- Check CORS headers

### 4. **Team ID Issue**
**Symptoms**: API returns error or empty data

**Causes**:
- Invalid Team ID
- Private team (can't access)
- Team doesn't exist

**How to verify**:
```bash
# Get team summary first
curl http://localhost:5000/api/team/123456/summary

# If this works, team ID is valid
```

## How Transfers Algorithm Works

```
1. Get your 11 current players
2. Get ALL available players in game
3. For each position (GK, DEF, MID, FWD):
   a. Filter available players NOT in your squad
   b. Filter only ACTIVE players (status='a')
   c. Score each: Form + Value + Ownership + Fixtures + Playing Time
   d. Return top 5 by score
4. Return organized by position
```

## Why You Might Get Empty Results Per Position

### GK (Goalkeeper) - Often empty
- Only ~20 GKs in Premier League
- If you have 2, only ~18 available
- After filtering inactive: maybe 15
- So usually 5+ options

**If empty**: Check if most GKs are injured or unavailable

### DEF (Defenders) - Usually has options
- ~100 defenders total
- Should have many options
- Rarely empty

**If empty**: Unusual - check FPL API status

### MID (Midfielders) - Largest pool
- ~150 midfielders
- Always has options
- Should never be empty

**If empty**: Something wrong with API

### FWD (Forwards) - Often empty
- ~50 forwards total
- Can run out if many unavailable
- More likely to be empty than other positions

**If empty**: Check if many forwards are injured

## Debug Steps

### Step 1: Check Backend Response

```bash
# Terminal 1: Start backend
cd backend
python run.py

# Terminal 2: Test endpoint
curl -s http://localhost:5000/api/recommendations/YOUR_TEAM_ID/transfers | python -m json.tool
```

**What to look for**:
```json
{
  "team_id": 123456,
  "recommendations": {
    "GK": [
      {
        "player_id": 5,
        "name": "Ederson",
        "score": 7.2,
        ...
      }
    ],
    "DEF": [...]  // should have 5
    "MID": [...]  // should have 5
    "FWD": [...]  // might be empty
  },
  "_debug": {
    "positions_with_recommendations": {
      "GK": 1,
      "DEF": 5,
      "MID": 5,
      "FWD": 0
    }
  }
}
```

### Step 2: Check Frontend Network

1. Open http://localhost:3000
2. Open DevTools (F12 → Network tab)
3. Enter your Team ID
4. Click "Best Transfers" tab
5. Look for request to `/api/recommendations/YOUR_TEAM_ID/transfers`
6. Check:
   - Status: Should be 200 (not 404, 403, 500)
   - Response: Should have `recommendations` object
   - Headers: Should have `Access-Control-Allow-Origin: *`

### Step 3: Check Browser Console

1. Open DevTools (F12 → Console tab)
2. Look for errors
3. Check if there are CORS errors

**CORS Error looks like**:
```
Access to XMLHttpRequest at 'http://localhost:5000/...' 
from origin 'http://localhost:3000' has been blocked by CORS policy
```

## Solutions

### If Backend Returns Empty Arrays

**Check what's available**:
```python
# Add this to recommendation_engine.py temporarily
available_players = [
    p for p in self.all_players
    if self._get_position_name(p.get('element_type', 0)) == 'GK'
    and p['id'] not in current_player_ids
    and p.get('status') == 'a'
]
print(f"Available GKs: {len(available_players)}")
```

### If CORS is blocked

Check that backend has:
```python
cors_config = {
    "origins": ["http://localhost:3000", "http://localhost:5000"],
    ...
}
CORS(app, resources={r"/api/*": cors_config})
```

### If team doesn't exist

Get valid team ID from:
- Go to https://fantasy.premierleague.com
- Log in
- View your team
- URL shows: `entry/{TEAM_ID}/`

## Expected Behavior

✅ **Working**:
- See 5 players per position (GK through FWD)
- Each shows: Name, Team, Price, Form, Score, Reason
- Player photos load
- Positions may have different counts (FWD often <5)

❌ **Not Working**:
- Empty positions (all showing nothing)
- Error messages
- No photos loading

## Manual Test Command

```bash
# Replace with your team ID
TEAM_ID=12345

# Get summary first (verify team exists)
curl -s http://localhost:5000/api/team/$TEAM_ID/summary | python -m json.tool

# Get transfers
curl -s http://localhost:5000/api/recommendations/$TEAM_ID/transfers | python -m json.tool

# Get differentials
curl -s http://localhost:5000/api/recommendations/$TEAM_ID/differentials | python -m json.tool
```

## Contact / Report Issue

If recommendations are truly empty after checking all above:

1. Save the JSON response from API
2. Note your Team ID
3. Check if multiple Team IDs have same issue
4. Report with details: Team ID, empty positions, API response

The app needs valid gameweek data - usually available during FPL season.
