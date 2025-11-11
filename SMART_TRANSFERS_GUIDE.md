# Smart Transfer Recommendations - Feature Guide

## Overview

The FPL Assistant now analyzes your actual squad and provides intelligent transfer suggestions based on underperformance, price efficiency, and upcoming fixture difficulty.

## Key Features

### 1. **Squad Overview Tab** 📋

View your complete current squad organized by position:

- **Players by Position**: GK, DEF, MID, FWD
- **Player Details**: Price, Form, Minutes Played
- **Special Badges**: 
  - 🔴 **C** - Captain
  - 🟠 **VC** - Vice Captain
- **Form Color Coding**:
  - 🔴 Red (0-2): Poor form
  - 🟠 Orange (3-4): Average form
  - 🟢 Green (5-10): Excellent form

**What It Shows:**
- Current squad composition
- Player performance metrics
- Playing time and form trends

---

### 2. **Smart Transfers Tab** 🔄

Automated analysis identifying underperforming players and suggesting specific swaps.

#### Underperformer Identification

The system analyzes each player and identifies those who are underperforming based on:

1. **Form Score** - Recent performance (0-10 scale)
2. **Expected vs Actual** - Points per game vs. form
3. **Playing Time** - Minutes played vs. expected
4. **Price Efficiency** - Cost relative to performance
5. **Ownership** - High-owned underperformers are more replaceable

#### Underperformance Scoring

```
Score = Expected_Points - Actual_Form

Where:
  Expected_Points = (Points_Per_Game × 3.0 / 90) × Minutes
  
Conditions for highlight:
  - Score > 1.0 (significantly underperforming)
  - Minutes < 90 AND Price > £5m (risky investment)
  - Not playing (0 minutes)
```

#### What You See

For each underperformer:
- **Reasons**: Why they're flagged (poor form, limited minutes, expensive, etc.)
- **Current Stats**: Price, form, minutes, ownership
- **Underperformance Score**: Higher = worse performer

---

### 3. **Smart Swap Suggestions** 💱

For each underperformer, the system suggests up to 3 replacement options:

#### Replacement Scoring Algorithm

```
Replacement_Score = 
  (Form × 0.40) +
  ((6 - FDR) / 5 × 0.30) +
  ((100 - Ownership) / 100 × 0.20) +
  (Minutes / 90 × 0.10)

Where:
  Form = Recent form (0-10)
  FDR = Fixture Difficulty Rating (1-5, lower = easier)
  Ownership = Selection % (lower = more unique)
  Minutes = Recent playing time
```

#### What Makes a Good Swap

1. **Similar or Better Form** - At least same level of performance
2. **Better Fixtures** - Lower FDR in upcoming 3 weeks
3. **Affordable** - Within budget (original price + transfer bank)
4. **Contrarian** - Lower ownership for mini-league edge
5. **Playing Time** - Regular starter with good minutes

#### Example Swap

```
SWAP OUT: Harry Maguire (£5.8m, Form 2.5, 0% form trend)
  ↓
SWAP IN OPTIONS:
  1. Virgil van Dijk (£6.0m, Form 7.2, FDR 2.2, 45% owned) ⭐ Best
  2. Kyle Walker (£5.8m, Form 6.5, FDR 2.4, 28% owned)
  3. Aaron Cresswell (£5.2m, Form 5.9, FDR 2.8, 12% owned) 🎯 Differential
```

---

## API Endpoints for Smart Transfers

### Get Transfer Analysis
```
GET /api/team/<team_id>/transfer-analysis
```

Returns:
- Current squad details
- Underperformers list
- Smart swaps per position

### Get Underperformers Only
```
GET /api/team/<team_id>/underperformers
```

Returns:
- List of underperforming players
- Underperformance scores and reasons

### Get Smart Swaps Per Position
```
GET /api/team/<team_id>/smart-swaps
```

Returns:
- Swap recommendations grouped by position
- Best replacement options for each underperformer

---

## How to Use

### Step 1: Enter Team ID
- Go to fantasy.premierleague.com and find your Team ID in the URL
- Example: `fantasy.premierleague.com/entry/123456/` → Team ID is **123456**

### Step 2: Click Squad Overview
- See your current team composition
- Identify players you want to upgrade

### Step 3: Click Smart Transfers
- System automatically analyzes underperformers
- Review the underperformance reasons
- See suggested replacements with scores

### Step 4: Make Decision
- Compare old vs new player
- Check price difference
- Verify upcoming fixtures
- Execute transfer in FPL app

---

## Example Scenario

### Your Squad
```
Gameweek 15
Rank: 50,000
Transfer Bank: £2.5m

DEF: Harry Maguire (£5.8m, Form 2.5) ❌ Underperforming
     Minutes: 0 (injured/benched)
     Reason: Not playing
```

### Smart Transfer Suggestion
```
REPLACE: Harry Maguire
BUDGET: £5.8m + £2.5m bank = £8.3m available

BEST OPTIONS:
1. Virgil van Dijk (£6.0m)
   - Form: 7.2 ⭐⭐⭐⭐⭐
   - FDR: 2.2 (easier fixtures)
   - Replacement Score: 7.8
   - Cost Diff: +£0.2m

2. Kyle Walker (£5.8m)
   - Form: 6.5 ⭐⭐⭐⭐
   - FDR: 2.4
   - Replacement Score: 7.2
   - Cost Diff: £0.0m (exact fit!)

3. Aaron Cresswell (£5.2m)
   - Form: 5.9 ⭐⭐⭐
   - FDR: 2.8
   - Replacement Score: 6.5
   - Ownership: 12% (Differential! 🎯)
   - Cost Diff: -£0.6m (save bank)
```

### Decision
- **Go for Virgil** = Premium pick, best form, better fixtures
- **Go for Kyle** = Same price, solid performer
- **Go for Aaron** = Save money, unique, decent form

---

## Advanced: Understanding the Metrics

### Form (0-10)
- Calculated from last 5 gameweeks
- Higher = better recent performance
- Used to predict immediate impact

### FDR (1-5)
- Fixture Difficulty Rating
- 1 = Easiest fixtures
- 5 = Hardest fixtures
- Looks at next 3 gameweeks

### Expected Points
- Based on player's historical PPG
- Normalized by minutes played
- Used to identify underperformers

### Ownership %
- % of FPL managers who own this player
- Lower = more unique (good for mini-leagues)
- Higher = safe pick (proven performer)

### Replacement Score
- Combined metric (0-10 scale)
- Higher = better swap
- Balances form, fixtures, ownership, minutes

---

## Tips for Best Transfers

### ✅ DO:
- Review upcoming fixtures (3-5 weeks ahead)
- Check injury/suspension status
- Consider ownership for mini-league strategy
- Transfer out highest underperformance scores
- Transfer in highest replacement scores

### ❌ DON'T:
- Make transfers without checking fixtures
- Chase form too aggressively (it changes)
- Ignore playing time (6 weeks of 0 mins = problem)
- Transfer too many players (use transfers wisely)
- Ignore team injuries/suspensions

---

## Common Questions

### Q: Why is my good player marked as underperformer?
**A:** Check:
- Recent form (has he been benched recently?)
- Minutes (is he getting played?)
- Price (expensive players need more points)
- Ownership (popular players are replaceable)

### Q: Why don't I see any swaps?
**A:** Possible reasons:
- Your squad is performing well (good sign!)
- No affordable replacements available
- Better players are all expensive
- Check your transfer bank status

### Q: Should I always take the highest-scored replacement?
**A:** Not necessarily:
- Consider fixtures (GW16-18 schedule matters)
- Think about mini-league strategy
- Balance premium (high form) vs differential (low ownership)
- Trust your intuition + the algorithm

### Q: How often should I use this?
**A:** Recommendations:
- Weekly: After gameweek ends
- Before deadline: Check underperformers
- When you get a free transfer
- During international breaks: Plan ahead

---

## Next Features Coming Soon

- 🚀 **Differential Alerts**: Automatic notifications for high-upside low-owned players
- 📊 **Transfer History**: Track performance of your transfers over time
- 🎯 **Mini-League Analysis**: Compare transfers with your league rivals
- 💡 **Injury Predictions**: Alert when players are likely to miss matches
- 🏆 **Chip Strategy**: Recommendations for Wildcard/Bench Boost/Free Hit

---

## Need Help?

Check the main README for:
- Setup instructions
- API documentation
- Architecture overview
- Troubleshooting

Happy transfers! ⚽🚀
