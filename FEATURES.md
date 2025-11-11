# FPL Assistant - Features Summary

## ✅ Complete Implementation

Your FPL Assistant now has **full functionality**! Here's what's available:

---

## 🎯 Main Features

### 1. **Team Analysis** (Overview Tab)
- **Input**: Team ID only (gameweek fetched automatically)
- **Displays**:
  - Total points and overall rank
  - Current gameweek
  - Transfers remaining
  - Transfer bank balance
  - Manager name and team name

### 2. **Best Transfer Recommendations** (Transfers Tab)
Get the best 5 transfer options for each position:

#### Per Position:
- **GK** (Goalkeepers) - Top 5 options
- **DEF** (Defenders) - Top 5 options
- **MID** (Midfielders) - Top 5 options
- **FWD** (Forwards) - Top 5 options

#### Info per Player:
- Player name & team
- Current price (£m)
- Recent form (0-10)
- Ownership percentage
- Expected points this week
- Upcoming fixture difficulty (FDR)
- **Recommendation score** - AI-calculated priority score
- **Reasoning** - Why they're recommended

#### Scoring Algorithm:
```
Score = (Form × 0.25) + 
         (Value × 0.20) + 
         (Contrarian Factor × 0.15) +
         (Fixtures × 0.25) +
         (Playing Time × 0.15)
```

---

### 3. **High-Upside Differentials** (Differentials Tab)
Discover 5 low-ownership players with high potential:

#### What are Differentials?
- Players owned by **<15% of managers**
- Good recent form but underrated
- Facing **easy upcoming fixtures**
- High potential for rank gains

#### Info per Differential:
- Player name & position
- Current price (£m)
- Recent form
- **Ownership % (highlighted if very low)**
- Differential score
- Expected points potential
- Reasoning

---

## 🚀 How to Use

### Step 1: Start the App
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python run.py

# Terminal 2 - Frontend
cd frontend
npm start
```

### Step 2: Find Your Team ID
- Go to https://fantasy.premierleague.com
- Log in to your team
- The URL will show: `https://fantasy.premierleague.com/entry/{TEAM_ID}/`
- Your Team ID is the number in the URL

### Step 3: Analyze Your Team
1. Open http://localhost:3000
2. Enter your **Team ID**
3. Click "Analyze Team"
4. Wait for data to load

### Step 4: Review Recommendations
- **Overview Tab**: Team summary and stats
- **Best Transfers Tab**: 
  - Review each position (GK, DEF, MID, FWD)
  - Check the recommendation score
  - Read the reason for each suggestion
- **Differentials Tab**:
  - Look for high differential_score
  - Focus on very low ownership % (<5%)
  - Consider for rank differentiation

---

## 📊 Understanding the Scores

### Transfer Recommendation Score (per position)
```
High Score (7.0+) = Strong recommendation
Medium Score (5.0-7.0) = Good option
Lower Score (3.0-5.0) = Consider if position needs improvement
```

**Factors considered:**
1. **Form** - Recent performance (0-10)
2. **Value** - Form per pound (good value = higher)
3. **Contrarian** - Low ownership = higher (unique edge)
4. **Fixtures** - Next 3 gameweeks difficulty
5. **Playing Time** - Minutes played recently

### Differential Score
```
High Score (7.0+) = Excellent differential
Medium Score (5.0-7.0) = Good differential
```

**Why these matter:**
- Low ownership + high score = rare advantage
- Help you differentiate from other managers
- Can swing mini-league positions

---

## 💡 Pro Tips

### Transfer Strategy
1. **Use Available Transfers Wisely**
   - You get ~1 free transfer per gameweek
   - Use chip wisely (Wildcard, Free Hit, etc.)

2. **Price Considerations**
   - Check transfer bank - do you have enough? (£m shown)
   - Look for value transfers first
   - Consider upcoming fixtures (FDR)

3. **Position Balance**
   - Standard squad: 2 GK, 5 DEF, 5 MID, 3 FWD
   - Adjust based on form and fixtures

### Differential Strategy
1. **Mini-League Competition**
   - Compare with opponents' teams
   - Pick differentials they don't have
   - High risk, high reward

2. **When to Use Differentials**
   - When behind in mini-league
   - Easy fixture for obscure player
   - 2-3 gameweeks before wildcards

3. **Own vs Differential Balance**
   - Don't load team with differentials
   - Mix safe picks with contrarian plays
   - 70% core, 30% differentials

---

## 🔄 Data Sources

All data comes from **FPL Official API**:
- Player stats updated daily
- Form recalculated each gameweek
- Fixture difficulty set by FPL
- Ownership updated throughout gameweek

---

## 📱 What's on Each Tab

### Overview Tab
```
├─ Team Stats (5 cards)
│  ├─ Total Points
│  ├─ Overall Rank
│  ├─ Current Gameweek
│  ├─ Transfers Remaining
│  └─ Transfer Bank Balance
└─ Instructions for other tabs
```

### Transfers Tab
```
├─ GK Card
│  └─ 5 Best Goalkeeper Options
├─ DEF Card
│  └─ 5 Best Defender Options
├─ MID Card
│  └─ 5 Best Midfielder Options
└─ FWD Card
   └─ 5 Best Forward Options

Each Player Shows:
├─ Name & Current Team
├─ Price
├─ Form (0-10)
├─ Ownership %
├─ Expected Points
├─ FDR Score
└─ AI Recommendation Reason
```

### Differentials Tab
```
├─ Card 1: Differential Player 1
├─ Card 2: Differential Player 2
├─ Card 3: Differential Player 3
├─ Card 4: Differential Player 4
└─ Card 5: Differential Player 5

Each Differential Shows:
├─ Name & Position
├─ Team & Price
├─ Form Score
├─ LOW Ownership % ⭐
├─ Differential Score
└─ Why it's a differential
```

---

## 🎮 Example Workflow

### Scenario: You're behind in mini-league

1. **Open FPL Assistant**
2. **Enter Team ID** and analyze
3. **Check Best Transfers**
   - Find underperforming players (low form)
   - Look for high-scoring replacements
4. **Check Differentials**
   - Find low-ownership gems
   - Compare with opponent's teams
5. **Make Decision**
   - Use transfer on either:
     - Safety: High-scoring popular player
     - Risk: Low-ownership differential
6. **Make the transfer on FPL.com**

---

## 🐛 Troubleshooting

### "Failed to fetch recommendations"
- Ensure backend is running (`python run.py`)
- Check Team ID is correct
- Verify internet connection to FPL API

### Recommendations taking long to load
- FPL API can be slow during peak times
- Try again in a few seconds
- ~2-3 seconds is normal

### Scores seem low
- If many players have form <3, squad is struggling
- Consider wildcarding or planning ahead
- Differentials may still offer value

---

## 🚀 What's Next?

Future enhancements:
- ✨ Multi-week transfer planning
- ✨ Chip strategy recommendations
- ✨ Historical performance tracking
- ✨ Injury prediction alerts
- ✨ League-specific benchmarking
- ✨ Mobile app version

---

## 📞 Support

Questions or issues?
1. Check this guide first
2. Verify backend is running
3. Check terminal for error messages
4. Review [SETUP_AND_USAGE.md](SETUP_AND_USAGE.md) for detailed setup

---

**Good luck with your FPL season! 🎯⚽**

Now you have:
✅ Automatic gameweek detection
✅ 5 transfers per position
✅ 5 differentials
✅ Multi-factor scoring
✅ Clean, intuitive UI
