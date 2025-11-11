# FPL Assistant - Setup & Usage Guide

## Quick Start

### 1. Backend Setup (Python/Flask)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env

# Run the server
python run.py
```

The backend API will be available at `http://localhost:5000`

### 2. Frontend Setup (React/TypeScript)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will be available at `http://localhost:3000`

---

## API Endpoints

### Team Analysis

#### Get Current Gameweek
```
GET /api/team/current-gameweek
```
Returns the current FPL gameweek.

**Response:**
```json
{
  "current_gameweek": 15
}
```

#### Get Team Summary
```
GET /api/team/<team_id>/summary
```
Get overview of a team by Team ID (only input required).

**Parameters:** `team_id` (integer)

**Response:**
```json
{
  "team_id": 123456,
  "team_name": "My FPL Team",
  "manager_name": "John Doe",
  "current_rank": 50000,
  "total_points": 850,
  "current_gameweek": 15,
  "transfers_remaining": 1,
  "transfer_bank": 2.5
}
```

#### Get Current Squad
```
GET /api/team/<team_id>/squad
```
Get full squad with player details.

**Response:**
```json
{
  "squad": [
    {
      "player_id": 1,
      "name": "Alisson",
      "position": "GK",
      "team": "LIV",
      "price": 5.0,
      "form": 5.2,
      "selected": 1,
      "captain": false,
      "vice_captain": false
    },
    ...
  ]
}
```

#### Get Squad Analysis
```
GET /api/team/<team_id>/analysis
```
Get squad form, position breakdown, and upcoming fixtures.

**Response:**
```json
{
  "total_squad_form": 4.8,
  "players_by_position": {
    "GK": {
      "count": 2,
      "avg_form": 5.1,
      "avg_price": 4.8,
      "players": [...]
    },
    "DEF": {...},
    "MID": {...},
    "FWD": {...}
  },
  "upcoming_fixtures": [
    {
      "gameweek": 15,
      "opponent": "MUN",
      "home": true,
      "difficulty": 4
    },
    ...
  ]
}
```

#### Get Detailed Analysis
```
GET /api/team/<team_id>/detailed-analysis
```
Get comprehensive analysis including squad depth and extended fixture info.

#### Get Squad Depth
```
GET /api/team/<team_id>/depth
```
Analyze squad depth, form distribution, and team concentration risks.

---

### Transfer Recommendations

#### Get Best Transfer Options Per Position
```
GET /api/recommendations/<team_id>/transfers
```
Get the best 5 transfer options for each position.

**Response:**
```json
{
  "team_id": 123456,
  "recommendations": {
    "GK": [
      {
        "player_id": 5,
        "name": "Ederson",
        "team": "MCI",
        "position": "GK",
        "price": 5.5,
        "form": 6.2,
        "selected_by_percent": 45.3,
        "minutes": 720,
        "expected_points_this_week": 6.5,
        "upcoming_fdr": 2.5,
        "value_score": 1.13,
        "ownership_score": 0.55,
        "fixture_score": 0.70,
        "playing_time_score": 1.0,
        "score": 6.2,
        "reason": "Good form (6.2) | Easy fixtures ahead (FDR 2.5)"
      },
      ...
    ],
    "DEF": [...],
    "MID": [...],
    "FWD": [...]
  }
}
```

**Scoring Breakdown:**
- **Form (25%)**: Recent performance (0-10 scale)
- **Value Score (20%)**: Form divided by price
- **Ownership Score (15%)**: Contrarian edge (100 - ownership %)
- **Fixture Difficulty (25%)**: Easier upcoming fixtures = higher score
- **Playing Time (15%)**: Likelihood of getting minutes

#### Get High-Upside Differentials
```
GET /api/recommendations/<team_id>/differentials
```
Get 5 low-ownership players with high potential.

**Response:**
```json
{
  "team_id": 123456,
  "differentials": [
    {
      "player_id": 150,
      "name": "Brennan Johnson",
      "team": "NOT",
      "position": "FWD",
      "price": 7.0,
      "form": 5.5,
      "selected_by_percent": 8.2,
      "ownership_rank": 8.2,
      "expected_points": 5.8,
      "upcoming_fdr": 2.8,
      "differential_score": 7.1,
      "reason": "Low ownership (8.2%) with form 5.5 and facing FDR 2.8"
    },
    ...
  ]
}
```

#### Get All Recommendations
```
GET /api/recommendations/<team_id>/all
```
Get transfers and differentials in one call.

**Response:**
```json
{
  "team_id": 123456,
  "data": {
    "current_gameweek": 15,
    "best_transfers_per_position": {...},
    "high_upside_differentials": [...]
  }
}
```

---

## How Recommendations Work

### Transfer Recommendations Algorithm

The engine scores each available player based on:

1. **Recent Form** - Last 5 gameweeks performance
2. **Price Value** - Form relative to current price (value for money)
3. **Ownership Contrarian Edge** - Low ownership = higher score
4. **Upcoming Fixture Difficulty (FDR)** - Easier fixtures = more potential points
5. **Expected Playing Time** - Minutes played ratio

### Differential Detection

Differentials are identified as players with:
- **Very Low Ownership** (<15%)
- **Good Recent Form** (>4.0)
- **Favorable Fixtures** (FDR <3.0)
- **Consistent Playing Time** (>60 minutes in last 3 games)

---

## Example: Full Workflow

```bash
# 1. Get current gameweek
curl http://localhost:5000/api/team/current-gameweek

# 2. Enter Team ID (e.g., 123456)
curl http://localhost:5000/api/team/123456/summary

# 3. Get recommendations
curl http://localhost:5000/api/recommendations/123456/transfers

# 4. Get differentials
curl http://localhost:5000/api/recommendations/123456/differentials

# 5. Get all at once
curl http://localhost:5000/api/recommendations/123456/all
```

---

## Features

✅ **Team ID Only Input** - Just enter your FPL Team ID, gameweek fetched automatically

✅ **Dynamic Gameweek Detection** - Always uses current FPL gameweek

✅ **5 Transfers Per Position** - Best options for GK, DEF, MID, FWD

✅ **5 High-Upside Differentials** - Low-ownership gems with potential

✅ **Multi-Factor Analysis** - Form, fixtures, ownership, value, playing time

✅ **Real-time Data** - Pulls live from FPL Official API

✅ **Contrarian Insights** - Identifies underowned players with high potential

---

## Technologies Used

- **Backend**: Flask, Python 3.8+, Requests
- **Frontend**: React 18, TypeScript, Axios
- **Data Source**: FPL Official API (https://fantasy.premierleague.com/api)
- **Deployment**: Ready for Docker containerization

---

## Troubleshooting

### "Failed to fetch team" error
- Check if Team ID is correct (get yours from fantasy.premierleague.com)
- Ensure backend server is running on port 5000
- Check FPL API is accessible

### CORS errors
- Backend has CORS enabled by default
- If issues persist, check Flask-CORS configuration

### "No recommendations found"
- May indicate all available players are expensive or low form
- Try checking with transfers endpoint for specific position

---

## Future Enhancements

- Machine learning models for predictive scoring
- Multi-week planning (chip strategy recommendations)
- Historical analysis and trend tracking
- Injury prediction alerts
- Integration with FPL mobile app
- Real-time chat for team discussion

---

## Support & Feedback

For issues or feature requests, please open an issue on GitHub.

Enjoy optimizing your FPL transfers! 🚀
