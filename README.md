# FPL Assistant

A comprehensive tool for analyzing Fantasy Premier League teams and recommending optimized transfers.

## 🎯 What is FPL Assistant?

**FPL Assistant** helps Fantasy Premier League managers make better transfer decisions by:

✅ **Analyzing any team** - Just enter Team ID, gameweek fetched automatically  
✅ **Finding best transfers** - Top 5 options per position (GK, DEF, MID, FWD)  
✅ **Discovering differentials** - 5 low-ownership players with high potential  
✅ **Multi-factor scoring** - Considers form, fixtures, value, ownership, playing time  
✅ **Real-time data** - Live FPL Official API integration  

---

## ⚡ Quick Start (2 minutes)

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm

### Setup

```bash
# Clone repo
git clone https://github.com/tymoteuszlenart/fpl_assistant.git
cd fpl_assistant

# Run quick start script
chmod +x quick-start.sh
./quick-start.sh

# OR manually:
# Terminal 1
cd backend && source venv/bin/activate && python run.py

# Terminal 2
cd frontend && npm start
```

Open **http://localhost:3000** in browser

---

## 📱 How to Use

1. **Get your Team ID**
   - Go to https://fantasy.premierleague.com
   - Log in and view your team
   - URL shows: `https://fantasy.premierleague.com/entry/{TEAM_ID}/`

2. **Enter Team ID**
   - Open the app
   - Enter your Team ID
   - Click "Analyze Team"

3. **Review Recommendations**
   - **Overview Tab** - Team stats summary
   - **Best Transfers Tab** - 5 options per position with scores
   - **Differentials Tab** - Low-ownership gems with potential

---

## 🌟 Key Features

### Transfer Recommendations

Get the **best 5 players per position** scored on:

```
Score = (Form × 0.25) + (Value × 0.20) + (Contrarian × 0.15) 
        + (Fixtures × 0.25) + (Playing Time × 0.15)
```

**What you see:**
- Player name, team, price
- Recent form (0-10)
- Ownership % (contrarian edge)
- Expected points & fixture difficulty
- **AI-calculated score** & reasoning

### Differentials

Find **5 high-upside players** with:
- Very low ownership (<15%)
- Good recent form
- Easy upcoming fixtures
- High potential for rank gains

**Perfect for:**
- Mini-league competition
- Gaining rank advantage
- When behind on points

---

## 📊 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Flask (Python), FPL API |
| **Frontend** | React 18, TypeScript 4.9 |
| **Styling** | CSS Grid, Flexbox |
| **Deployment** | Docker, Docker Compose |

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| [FEATURES.md](FEATURES.md) | Detailed feature guide |
| [SETUP_AND_USAGE.md](SETUP_AND_USAGE.md) | Installation & API endpoints |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical architecture |
| [UI_GUIDE.md](UI_GUIDE.md) | Visual guide & UI walkthrough |

---

## 🎮 Example

### Scenario: You're behind in mini-league

```
1. Enter Team ID → App loads
2. Check "Best Transfers" → Find underperforming players
3. Check "Differentials" → Find unique low-ownership picks
4. Compare recommendations vs opponent teams
5. Make strategic transfer on FPL.com
```

---

## 🔄 API Endpoints

### Team Analysis
```
GET /api/team/current-gameweek
GET /api/team/<team_id>/summary
GET /api/team/<team_id>/squad
GET /api/team/<team_id>/analysis
GET /api/team/<team_id>/detailed-analysis
GET /api/team/<team_id>/depth
```

### Recommendations
```
GET /api/recommendations/<team_id>/transfers      # 5 per position
GET /api/recommendations/<team_id>/differentials  # 5 differentials
GET /api/recommendations/<team_id>/all            # Combined
```

See [SETUP_AND_USAGE.md](SETUP_AND_USAGE.md) for full API reference.

---

## 🐳 Docker

Run everything with Docker:

```bash
docker-compose up
```

Starts:
- Backend on `http://localhost:5000`
- Frontend on `http://localhost:3000`

---

## 🚀 Project Structure

```
fpl_assistant/
├── backend/
│   ├── app/
│   │   ├── routes/           # API endpoints
│   │   ├── services/         # Business logic
│   │   └── utils/            # FPL API client
│   ├── requirements.txt
│   └── run.py               # Entry point
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   └── App.tsx           # Main app
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## 💡 Understanding Scores

### Transfer Recommendation Score
```
7.0+ = Excellent recommendation
5.0-7.0 = Good option
3.0-5.0 = Consider if needed
```

**Why these factors?**
- **Form (25%)** - Recent performance matters most
- **Value (20%)** - Get points per pound spent
- **Contrarian (15%)** - Unique edge in mini-leagues
- **Fixtures (25%)** - Easy games = more points
- **Playing Time (15%)** - Must get minutes

### Differential Score
- Low ownership (40% weight)
- Good form (35% weight)
- Easy fixtures (25% weight)

---

## 🎯 Pro Tips

### Using Transfer Recommendations
1. Check **highest scores first** in each position
2. Verify you have enough **transfer bank** (£m shown)
3. Consider **position depth** - don't overload one position
4. Mix **safety** (high-scoring popular) with **risk** (differentials)

### Using Differentials
1. Compare with **mini-league opponent teams**
2. Look for **very low ownership** (<5%)
3. Balance **core team** (70%) with **differentials** (30%)
4. Use when **behind** for maximum impact

### When to Transfer
- Use free transfer on weakest position
- Wildcard when 3+ underperformers
- Free Hit for unexpected emergencies
- Plan chips 2-3 weeks ahead

---

## 🔗 Links

- **FPL Official**: https://fantasy.premierleague.com
- **FPL Stats**: https://fplreview.com
- **Community**: r/FantasyPL

---

## 📝 Data Sources

All data from **FPL Official API**:
- Player stats updated daily
- Form recalculated each gameweek
- Fixture difficulty set by FPL
- Ownership updated live

---

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| Failed to fetch | Ensure backend running on :5000 |
| CORS errors | Backend has CORS enabled by default |
| Slow loading | FPL API can be slow during peak times |
| Wrong Team ID | Verify from fantasy.premierleague.com URL |

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Machine learning predictions
- Multi-week planning
- Injury alerts
- Mobile app
- Advanced analytics

---

## 📄 License

MIT License - See LICENSE file

---

## ⚠️ Disclaimer

**For entertainment purposes only**
- This tool supports decision-making, not financial advice
- Past form doesn't guarantee future performance
- Use recommendations as guide, not absolute truth
- FPL carries financial risk
- Author not responsible for gains/losses

---

## 🎉 Ready to Dominate?

1. **Get your Team ID** from FPL
2. **Run the app** (`./quick-start.sh`)
3. **Analyze your team**
4. **Review recommendations**
5. **Make transfers on FPL.com**
6. **Climb the ranks! 📈**

---

**Questions?** Check [SETUP_AND_USAGE.md](SETUP_AND_USAGE.md) or [FEATURES.md](FEATURES.md)

**Good luck this FPL season! ⚽🏆**
