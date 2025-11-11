# Architecture Overview

## Project Structure

```
fpl_assistant/
├── backend/                          # Python Flask Backend
│   ├── app/
│   │   ├── __init__.py              # Flask app factory
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── team_routes.py       # Team analysis endpoints
│   │   │   └── recommendation_routes.py  # Recommendation endpoints
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── team_analyzer.py     # Team analysis logic
│   │   │   └── recommendation_engine.py  # Recommendation algorithms
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── fpl_api.py           # FPL API client
│   ├── run.py                       # Entry point
│   ├── requirements.txt             # Python dependencies
│   └── .env.example                # Environment template
│
├── frontend/                        # React TypeScript Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── TeamSearch.tsx       # Team search component
│   │   │   ├── TeamSearch.css
│   │   │   ├── TeamAnalysis.tsx     # Analysis display
│   │   │   └── TeamAnalysis.css
│   │   ├── App.tsx                  # Main app component
│   │   ├── App.css
│   │   ├── index.tsx                # React entry point
│   │   └── index.css
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   └── tsconfig.json
│
├── Dockerfile.backend               # Backend container
├── Dockerfile.frontend              # Frontend container
├── docker-compose.yml               # Multi-container setup
├── README.md                        # Main documentation
├── SETUP_AND_USAGE.md              # Detailed guide
└── ARCHITECTURE.md                 # This file
```

## Data Flow

```
User Input (Team ID)
        ↓
Frontend (React)
        ↓
API Gateway (Flask)
        ↓
TeamAnalyzer Service
        ├── Fetch Team Data (FPL API)
        ├── Fetch Squad Picks (FPL API)
        ├── Fetch Bootstrap Data (FPL API)
        └── Analyze & Structure
        ↓
RecommendationEngine Service
        ├── Score Available Players
        ├── Rank by Position
        ├── Identify Differentials
        └── Generate Reasoning
        ↓
Response JSON
        ↓
Frontend Display
        ↓
User Decision Making
```

## API Architecture

### REST Endpoints

**Team Analysis:**
```
GET /api/team/current-gameweek           → Get current GW
GET /api/team/<team_id>/summary          → Team overview
GET /api/team/<team_id>/squad            → Current squad
GET /api/team/<team_id>/analysis         → Squad analysis
GET /api/team/<team_id>/detailed-analysis → Full analysis
GET /api/team/<team_id>/depth            → Position depth
```

**Recommendations:**
```
GET /api/recommendations/<team_id>/transfers     → 5 per position
GET /api/recommendations/<team_id>/differentials → 5 differentials
GET /api/recommendations/<team_id>/all           → All recommendations
```

## Recommendation Algorithm

### Score Calculation (RecommendationEngine._score_player_for_transfer)

```
Final Score = 
  (Form × 0.25) +
  (Value_Score × 0.20) +
  (Ownership_Score × 0.15) +
  (Fixture_Score × 0.25) +
  (Playing_Time_Score × 0.15)

Where:
  Form = Player's form (0-10)
  Value_Score = Form / Price
  Ownership_Score = (100 - Selected_Percent) / 100
  Fixture_Score = (6 - FDR) / 5
  Playing_Time_Score = Minutes / 90
```

### Differential Detection

```
Differential_Score =
  (Form × 0.35) +
  (Ownership_Factor × 0.40) +
  (Fixture_Factor × 0.25)

Requirements:
  - Selected by <15%
  - Form >4.0
  - FDR <3.0
  - Playing time >60 mins recent
```

## External Dependencies

### FPL Official API
- **Base URL**: https://fantasy.premierleague.com/api
- **Endpoints Used**:
  - `/bootstrap-static/` - Teams, players, positions, gameweeks
  - `/entry/{team_id}/` - Team details
  - `/entry/{team_id}/event/{gameweek}/picks/` - Squad for gameweek
  - `/element/{player_id}/` - Player details
  - `/fixtures/` - All fixtures

### Rate Limiting
- No official rate limit published
- Caching implemented via `@lru_cache` for bootstrap data
- Consider implementing request queuing for production

## Key Design Decisions

1. **Team ID Only Input**
   - Simpler UX (no gameweek selector needed)
   - Current gameweek fetched dynamically
   - Always provides latest analysis

2. **Position-Based Recommendations**
   - Users need clarity on which position to improve
   - Standard FPL positions: GK, DEF, MID, FWD
   - 5 options per position = manageable choice set

3. **Contrarian Scoring**
   - Ownership factor (15-40% weight) identifies differential opportunities
   - Balance between form and uniqueness
   - Helps in competitive mini-leagues

4. **Fixture Difficulty Rating (FDR)**
   - Official FPL metric (1-5 scale)
   - Next 3-5 gameweeks considered
   - Major factor in form normalization

5. **Microservice Architecture**
   - TeamAnalyzer focuses on current state
   - RecommendationEngine focuses on recommendations
   - Easy to add new services (injuries, chip strategy, etc.)

## Performance Considerations

### Caching
```python
@lru_cache(maxsize=128)
def get_bootstrap_static()  # Bootstrap data cached for session
```

### API Calls per Request
- 1x bootstrap-static (cached)
- 1x entry/{team_id}/
- 1x entry/{team_id}/event/{gameweek}/picks/
- 1x fixtures/ (cached)
- **Total**: 2-4 API calls per analysis request

### Response Time
- Typical: 1-3 seconds (bottleneck is FPL API)
- Could be optimized with database caching
- Consider Redis for production

## Scaling Recommendations

### For Production

1. **Database Layer**
   - Cache player data (updated weekly)
   - Store historical performance
   - Enable rapid recommendations

2. **Message Queue**
   - Async recommendation generation
   - Batch processing for leagues

3. **Rate Limiting**
   - Implement API rate limiting
   - User quotas for free tier

4. **Monitoring**
   - Error tracking (Sentry)
   - Performance monitoring (DataDog)
   - User analytics

5. **Containerization**
   - Docker images provided
   - Docker Compose for local dev
   - Kubernetes ready

## Testing Strategy

### Unit Tests (Frontend)
```
src/components/__tests__/
  ├── TeamSearch.test.tsx
  └── TeamAnalysis.test.tsx
```

### Integration Tests (Backend)
```
backend/tests/
  ├── test_team_analyzer.py
  ├── test_recommendation_engine.py
  └── test_routes.py
```

### E2E Tests
- Selenium for full workflow testing
- Mock FPL API for consistent results

## Future Architecture Enhancements

1. **Machine Learning**
   - Predictive models for player performance
   - Historical trend analysis
   - Transfer success prediction

2. **Real-time Updates**
   - WebSocket for live price changes
   - Injury alerts
   - Breaking news integration

3. **Advanced Features**
   - Multi-week planning
   - Chip strategy optimizer
   - League-specific tactics

4. **Mobile App**
   - React Native version
   - Push notifications
   - Offline support

5. **Premium Features**
   - Advanced analytics dashboard
   - Historical performance tracking
   - AI-powered recommendations
   - API access for third-party tools

## Deployment

### Local Development
```bash
# Backend
cd backend && python run.py

# Frontend
cd frontend && npm start
```

### Docker
```bash
docker-compose up
```

### Cloud Deployment
- AWS: ECS + RDS
- GCP: Cloud Run + Firestore
- Heroku: Simple git push deployment
- DigitalOcean: App Platform

---

See [SETUP_AND_USAGE.md](SETUP_AND_USAGE.md) for installation and usage instructions.
