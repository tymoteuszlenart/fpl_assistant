# Directory Structure - Organized

## Root Level (Essential Files Only)

```
fpl_assistant/
├── .git/                    # Git repository
├── .gitignore              # Git ignore rules
├── README.md               # Main project documentation
├── docker-compose.yml      # Docker orchestration
├── Dockerfile.backend      # Backend container
├── Dockerfile.frontend     # Frontend container
├── quick-start.sh          # Unix/Mac quick start
├── quick-start.bat         # Windows quick start
├── backend/                # Python Flask backend
├── frontend/               # React TypeScript frontend
└── docs/                   # Documentation (organized)
```

## Documentation Structure (`/docs`)

```
docs/
├── setup/
│   ├── SETUP_AND_USAGE.md
│   │   └── Full installation guide, API endpoints, troubleshooting
│   └── TYPESCRIPT_CRA_COMPATIBILITY.md
│       └── TypeScript 4.9.5 with React 18 configuration
│
├── api/
│   ├── ARCHITECTURE.md
│   │   └── System architecture, data flow, algorithms, scaling
│   ├── CORS_CONFIGURATION.md
│   │   └── CORS setup, headers, production config
│   └── PHOTOS_FIX.md
│       └── Photo proxy endpoint, 403 fix, backend setup
│
├── features/
│   ├── FEATURES_GUIDE.md
│   │   └── All features with examples and use cases
│   ├── SMART_TRANSFERS_GUIDE.md
│   │   └── Smart swaps algorithm, urgency scoring, improvements
│   └── UI_GUIDE.md
│       └── Visual walkthrough, all 5 tabs, components
│
└── guides/
    ├── QUICK_REFERENCE.md
    │   └── 60-second setup, endpoints, pro tips, colors, metrics
    └── TESTING_GUIDE.md
        └── Testing procedures, QA checklist, deployment readiness
```

## File Organization by Category

### Setup Documentation
- `docs/setup/SETUP_AND_USAGE.md` - How to install and use
- `docs/setup/TYPESCRIPT_CRA_COMPATIBILITY.md` - TypeScript 4.9.5 config

### API Documentation
- `docs/api/ARCHITECTURE.md` - Technical system design
- `docs/api/CORS_CONFIGURATION.md` - Cross-origin configuration
- `docs/api/PHOTOS_FIX.md` - Photo proxy implementation

### Feature Documentation
- `docs/features/FEATURES_GUIDE.md` - Complete feature walkthrough
- `docs/features/SMART_TRANSFERS_GUIDE.md` - Smart swaps explained
- `docs/features/UI_GUIDE.md` - User interface guide

### Quick Reference
- `docs/guides/QUICK_REFERENCE.md` - Fast lookup guide
- `docs/guides/TESTING_GUIDE.md` - QA and testing

## Backend Structure

```
backend/
├── app/
│   ├── __init__.py              # Flask app factory + CORS config
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── team_routes.py       # GET /api/team/...
│   │   ├── recommendation_routes.py  # GET /api/recommendations/...
│   │   └── photo_routes.py      # GET /api/photos/{code}.png
│   ├── services/
│   │   ├── __init__.py
│   │   ├── team_analyzer.py     # Team analysis logic
│   │   ├── recommendation_engine.py  # Transfer scoring
│   │   └── squad_transfer_analyzer.py  # Smart swaps
│   └── utils/
│       ├── __init__.py
│       └── fpl_api.py           # FPL API client (with User-Agent)
├── run.py                       # Entry point
├── requirements.txt             # Python dependencies
└── .env.example                # Environment template
```

## Frontend Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── TeamSearch.tsx       # Team ID input form
│   │   ├── TeamSearch.css       # Search styling
│   │   ├── TeamAnalysis.tsx     # 5-tab main component
│   │   └── TeamAnalysis.css     # All tab styling
│   ├── App.tsx                  # Root component
│   ├── App.css                  # Global styles
│   ├── index.tsx                # React entry point
│   └── index.css                # Base styles
├── public/
│   └── index.html               # HTML template
├── package.json                 # npm dependencies
└── tsconfig.json                # TypeScript config
```

## What Changed

### Before (Cluttered)
```
root/
├── ARCHITECTURE.md
├── CHECKLIST.md
├── CORS_CONFIGURATION.md
├── FEATURES.md
├── FEATURES_GUIDE.md
├── IMPLEMENTATION_COMPLETE.md
├── IMPLEMENTATION_SUMMARY.md
├── PHOTOS_FIX.md
├── PROJECT_STATUS.md
├── QUICK_REFERENCE.md
├── README.md
├── SETUP_AND_USAGE.md
├── SMART_TRANSFERS_GUIDE.md
├── SMART_TRANSFERS_IMPLEMENTATION.md
├── TESTING_GUIDE.md
├── TYPESCRIPT_CRA_COMPATIBILITY.md
├── UI_GUIDE.md
├── UI_UX_ENHANCEMENTS.md
└── ... (many more files)
```

### After (Organized)
```
root/
├── README.md
├── docker-compose.yml
├── quick-start.sh
├── docs/
│   ├── setup/
│   ├── api/
│   ├── features/
│   └── guides/
├── backend/
└── frontend/
```

## Benefits

✅ **Cleaner root directory** - Only essential files visible  
✅ **Logical organization** - Docs grouped by category  
✅ **Easy navigation** - Know where to look for what  
✅ **Better onboarding** - New developers find docs easily  
✅ **Scalable structure** - Easy to add new docs without clutter  
✅ **Professional appearance** - Clean project structure  

## How to Find Documentation

### "I want to..."
| Goal | Location |
|------|----------|
| **Set up the project** | `docs/setup/SETUP_AND_USAGE.md` |
| **Understand the architecture** | `docs/api/ARCHITECTURE.md` |
| **Learn all features** | `docs/features/FEATURES_GUIDE.md` |
| **Fix photos** | `docs/api/PHOTOS_FIX.md` |
| **Quick reference** | `docs/guides/QUICK_REFERENCE.md` |
| **Configure CORS** | `docs/api/CORS_CONFIGURATION.md` |
| **Test the app** | `docs/guides/TESTING_GUIDE.md` |
| **TypeScript issues** | `docs/setup/TYPESCRIPT_CRA_COMPATIBILITY.md` |
| **Smart swaps explained** | `docs/features/SMART_TRANSFERS_GUIDE.md` |
| **UI walkthrough** | `docs/features/UI_GUIDE.md` |

## Adding New Documentation

1. **Decide category**: setup, api, features, or guides
2. **Create file** in appropriate `/docs/{category}/` folder
3. **Update README.md** with link if needed
4. **Use relative links** for navigation between docs

## Notes

- Old root-level doc files can be deleted after migration
- All content preserved, just reorganized
- Links in README updated to new paths
- Each doc stands alone but references others where needed
