````markdown
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
│   │   │   ├── recommendation_routes.py  # Recommendation endpoints
│   │   │   └── photo_routes.py      # Photo proxy endpoint
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── team_analyzer.py     # Team analysis logic
│   │   │   ├── recommendation_engine.py  # Recommendation algorithms
│   │   │   └── squad_transfer_analyzer.py  # Smart swaps logic
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── fpl_api.py           # FPL API client with User-Agent
│   ├── run.py                       # Entry point
│   ├── requirements.txt             # Python dependencies
│   └── .env.example                # Environment template
│
├── frontend/                        # React TypeScript Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── TeamSearch.tsx       # Team search component
│   │   │   ├── TeamSearch.css
│   │   │   ├── TeamAnalysis.tsx     # 5-tab analysis display
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
├── docs/                            # Documentation
│   ├── setup/                       # Setup guides
│   │   ├── SETUP_AND_USAGE.md
│   │   └── TYPESCRIPT_CRA_COMPATIBILITY.md
│   ├── api/                         # API documentation
│   │   ├── ARCHITECTURE.md
│   │   ├── CORS_CONFIGURATION.md
│   │   └── PHOTOS_FIX.md
│   ├── features/                    # Feature guides
│   │   ├── FEATURES_GUIDE.md
│   │   ├── SMART_TRANSFERS_GUIDE.md
│   │   └── UI_GUIDE.md
│   └── guides/                      # Quick guides
│       ├── QUICK_REFERENCE.md
│       └── TESTING_GUIDE.md
│
├── Dockerfile.backend               # Backend container
├── Dockerfile.frontend              # Frontend container
├── docker-compose.yml               # Multi-container setup
├── README.md                        # Main documentation
├── quick-start.sh                   # Quick start script
└── quick-start.bat                  # Windows quick start
```

## Data Flow

```
User Input (Team ID)
        ↓
Frontend (React - Port 3000)
        ↓
API Gateway (Flask - Port 5000) with CORS
        ↓
TeamAnalyzer Service
        ├── Fetch Team Data (FPL API + User-Agent)
        ├── Fetch Squad Picks (FPL API + User-Agent)
        ├── Fetch Bootstrap Data (FPL API + User-Agent)
        └── Analyze & Structure
        ↓
RecommendationEngine Service
        ├── Score Available Players (5 factors)
        ├── Rank by Position
        ├── Identify Differentials
        └── Generate Reasoning
        ↓
SquadTransferAnalyzer Service
        ├── Calculate Urgency Scores
        ├── Find Underperformers
        ├── Find Best Replacements
        └── Generate Smart Swaps
        ↓
Photo Proxy Endpoint
        ├── Fetch from FPL API
        ├── Add CORS Headers
        └── Serve to Frontend
        ↓
Response JSON with Photo URLs
        ↓
Frontend Display (5 Tabs)
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
GET /api/team/<team_id>/squad-overview   → Squad with photos & ratings
```

**Recommendations:**
```
GET /api/recommendations/<team_id>/transfers     → 5 per position
GET /api/recommendations/<team_id>/differentials → 5 differentials (organized by position)
GET /api/team/<team_id>/smart-swaps              → Smart swaps (max 5 per position)
```

**Photos (Proxy):**
```
GET /api/photos/<player_code>.png   → Player photo from FPL API
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
  (Form × 0.30) +
  (Ownership_Factor × 0.40) +
  (Fixture_Factor × 0.20) +
  (Playing_Time × 0.10)

Requirements:
  - Selected by <15%
  - Form >4.0
  - FDR <3.0
  - Playing time >60 mins recent
```

### Smart Swaps (SquadTransferAnalyzer)

```
Urgency_Score for Current Players =
  (Not_Playing × 2.0) +
  (Poor_Form × 1.0) +
  (Expensive_Low_Form × 0.5)

Then for each underperformer:
  - Find replacements at same/lower price
  - Calculate improvement_vs_current
  - Show top 5 replacements ordered by improvement
  - Max 5 underperformers per position ordered by urgency
```

## External Dependencies

### FPL Official API
- **Base URL**: https://fantasy.premierleague.com/api
- **User-Agent Header**: Required (added to all requests)
- **Endpoints Used**:
  - `/bootstrap-static/` - Teams, players, positions, gameweeks
  - `/entry/{team_id}/` - Team details
  - `/entry/{team_id}/event/{gameweek}/picks/` - Squad for gameweek
  - `/element/{player_id}/` - Player details
  - `/fixtures/` - All fixtures

### CORS Configuration
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:5000/api/*`
- Photo endpoint: Explicit CORS headers on all responses
- Production: Update domain names

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

4. **Smart Swaps - Urgency Focused**
   - Not playing = highest priority for swap
   - Poor form = high priority
   - Calculates improvement potential vs current player
   - Only suggests meaningful upgrades

5. **Photo Proxy Endpoint**
   - Backend proxies images from FPL API
   - Adds User-Agent header to bypass 403
   - CORS headers ensure frontend can load images
   - Future: Can add caching/CDN layer

6. **Microservice Architecture**
   - TeamAnalyzer: Current squad state
   - RecommendationEngine: Transfer recommendations
   - SquadTransferAnalyzer: Smart swaps
   - Easy to add new services (injuries, chip strategy, etc.)

## Performance Considerations

### Caching
```python
@lru_cache(maxsize=128)
def get_bootstrap_static()  # Bootstrap data cached per session
```

### API Calls per Request
- 1x bootstrap-static (cached)
- 1x entry/{team_id}/
- 1x entry/{team_id}/event/{gameweek}/picks/
- 1x fixtures/ (cached)
- **Total**: 2-4 API calls per analysis request

### Response Time
- Typical: 1-3 seconds (bottleneck is FPL API)
- Photo loading: Async on frontend
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

4. **Photo CDN**
   - Cache proxied photos
   - Serve from CDN for speed

5. **Monitoring**
   - Error tracking (Sentry)
   - Performance monitoring (DataDog)
   - User analytics

6. **Containerization**
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
  ├── test_squad_transfer_analyzer.py
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

See [docs/setup/SETUP_AND_USAGE.md](../setup/SETUP_AND_USAGE.md) for installation and usage instructions.

````
