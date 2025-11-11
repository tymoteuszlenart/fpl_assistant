# 🎯 Quick Reference - FPL Assistant

## 60-Second Setup

### Backend:
```bash
cd backend && python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

### Frontend:
```bash
cd frontend
npm install
npm start
```

**Done!** 🚀 Open http://localhost:3000

---

## 5 Tabs Explained

| Tab | Purpose | What You See |
|-----|---------|--------------|
| 📊 **Overview** | Team stats | Rank, points, transfers left, bank balance |
| 👥 **Squad** | Current players | All 11 players with photos, form, value |
| 🔄 **Smart Swaps** | Specific trades | "Remove X, add Y" recommendations |
| ⭐ **Best Transfers** | Position options | 5 best per position in 2x2 tiles |
| 💎 **Differentials** | Low-ownership | 5 per position, organized by rarity |

---

## The Scoring Algorithm

```
Score = Form(25%) + Value(20%) + Ownership(15%) + Fixtures(25%) + Minutes(15%)
```

**Simple Translation:**
- Recent good performance? ✅
- Cheap relative to points? ✅
- Underowned (contrarian edge)? ✅
- Easy upcoming fixtures? ✅
- Getting playing time? ✅

---

## API Endpoints Cheat Sheet

```
# Team Data
GET /api/team/current-gameweek
GET /api/team/{id}/summary
GET /api/team/{id}/squad
GET /api/team/{id}/squad-overview
GET /api/team/{id}/smart-swaps

# Recommendations
GET /api/recommendations/{id}/transfers
GET /api/recommendations/{id}/differentials
GET /api/recommendations/{id}/all
```

---

## Common Questions

**Q: How do I find my Team ID?**
A: Go to fantasy.premierleague.com, it's in the URL: `fantasy.premierleague.com/entry/{ID}/`

**Q: Why no gameweek selector?**
A: It detects current GW automatically! Always up-to-date.

**Q: What's a "differential"?**
A: A player owned by <15% of managers. Great for winning mini-leagues!

**Q: How often do recommendations update?**
A: Real-time! Every time you click, it fetches fresh FPL API data.

**Q: Can I use this on mobile?**
A: Yes! Fully responsive design works on all devices.

---

## Feature Highlights

✅ **Photos** - Player images in squad & recommendations
✅ **Smart Tiles** - 2x2 grid layout for easy browsing  
✅ **Position Grouped** - Differentials organized by role
✅ **Top 5 Only** - Smart swaps limited to most profitable
✅ **Multiple Scores** - Value, form, fixtures all factored in

---

## Docker Quick Start

```bash
# Start both backend & frontend
docker-compose up

# Backend: http://localhost:5000
# Frontend: http://localhost:3000
```

---

## File Structure for Dev

```
Key Files:
- backend/app/services/recommendation_engine.py      → Scoring logic
- backend/app/services/squad_transfer_analyzer.py    → Swap logic  
- frontend/src/components/TeamAnalysis.tsx          → UI display
- frontend/src/components/TeamAnalysis.css          → Styling
```

---

## Troubleshooting in 30 Seconds

| Problem | Solution |
|---------|----------|
| "Team not found" | Check Team ID is correct |
| "CORS error" | Backend might not be running on :5000 |
| "No photos" | Check internet connection (fetches from FPL) |
| "Slow loading" | FPL API might be rate-limited, try again |
| "Mobile broken" | Clear browser cache & reload |

---

## Performance Tips

- 🟢 Fresh app load: ~3 seconds
- 🟢 Tab switching: ~2 seconds (cached)
- 🟢 Squad view: Photos lazy-load as needed
- 🟢 Best when run on broadband

---

## Color Meanings

| Color | Meaning |
|-------|---------|
| 🟢 Green | Excellent performance |
| 🔵 Blue | Good performance |
| 🟠 Orange | Average performance |
| 🔴 Red | Poor performance |

---

## Key Metrics Per Player

| Metric | Meaning |
|--------|---------|
| **Score** | Overall recommendation strength (0-10) |
| **Form** | Last 5 gameweeks performance |
| **Owned %** | % of FPL managers with player |
| **FDR** | Fixture Difficulty Rating (1=easy, 5=hard) |
| **pts/£m** | Points earned per million spent |

---

## Top Tips for Users

1. **Check Differentials First** - Best way to gain league edge
2. **Look for Value** - High pts/£m = underpriced
3. **Consider Bank** - Ensure you can afford recommended transfers
4. **Check Injuries** - App doesn't factor injuries yet
5. **Combine Analysis** - Use Smart Swaps + Best Transfers together

---

## Tech Stack Summary

- **Backend**: Python Flask (REST API)
- **Frontend**: React + TypeScript (Single Page App)
- **Data**: FPL Official API
- **Deployment**: Docker / Docker Compose
- **Styling**: CSS3 Responsive Grid

---

## What's NOT Included

❌ Injury predictions
❌ Chip strategy recommendations
❌ Captain/bench suggestions
❌ Price movement forecasts
❌ User accounts / saved analyses

*(Great features for future versions!)*

---

## Production Checklist

- ✅ No console errors
- ✅ No TypeScript errors
- ✅ Mobile responsive tested
- ✅ API endpoints working
- ✅ Docker builds successfully
- ✅ Error handling in place
- ✅ Environment variables ready
- ✅ Documentation complete

---

## Next Steps

1. **Try it out** - Enter Team ID and explore
2. **Compare with FPL** - Verify recommendations make sense
3. **Make transfers** - Use recommendations for real decisions
4. **Give feedback** - Report bugs or feature ideas
5. **Share it** - Tell other managers about the tool

---

**Questions? Check the docs:**
- 📖 **Setup**: SETUP_AND_USAGE.md
- 🏗️ **Architecture**: ARCHITECTURE.md
- ✨ **Features**: FEATURES_GUIDE.md
- 🧪 **Testing**: TESTING_GUIDE.md

---

**Happy FPL-ing! 🎯⚽**
