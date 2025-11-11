# FPL Assistant - Testing Guide

## Quick Start for Testing

### Prerequisites
- Python 3.8+
- Node.js 14+
- Already ran setup from quick-start script

### Starting the App

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or: venv\Scripts\activate on Windows
python run.py
```
Should see: `Running on http://127.0.0.1:5000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```
Should see: `Compiled successfully!` and browser opens to http://localhost:3000

---

## Testing Steps

### Test 1: Basic Team Lookup

**Input:** Team ID `1` (official test team) or your own team ID

**Expected Output:**
- Summary shows team name, manager, rank, points
- 5 stat cards populated with data

**Pass Criteria:** ✅ All fields filled with real data

---

### Test 2: Squad Tab

**Steps:**
1. Click "Squad" tab
2. Wait for data to load

**Expected Output:**
- Squad summary (total spent, bank, squad form)
- Players grouped by position
- Each player shows: name, team, price, form, value
- Color-coded performance badges

**Pass Criteria:** ✅ All players visible with correct grouping

---

### Test 3: Smart Swaps Tab

**Steps:**
1. Click "Smart Swaps" tab
2. Wait for data to load

**Expected Output:**
- Position sections (GK, DEF, MID, FWD)
- For each position with underperformers:
  - Player to remove with reason
  - 1-3 replacement options
  - Each option shows team, price, reason

**Pass Criteria:** ✅ Swap suggestions appear with reasoning

---

### Test 4: Transfers Tab

**Steps:**
1. Click "Transfers" tab
2. Wait for data to load

**Expected Output:**
- 4 position sections (GK, DEF, MID, FWD)
- Each position has up to 5 players
- Each player shows:
  - Score badge (top right)
  - Team badge
  - Price (£m)
  - Form
  - FDR (fixture difficulty)
  - Reasoning

**Pass Criteria:** ✅ All positions have recommendations

---

### Test 5: Differentials Tab

**Steps:**
1. Click "Differentials" tab
2. Wait for data to load

**Expected Output:**
- Grid of 5 differential cards
- Each card shows:
  - Player name
  - Position (GK/DEF/MID/FWD)
  - Team
  - Score
  - Price
  - Ownership % (should be LOW)
  - Form
  - FDR

**Pass Criteria:** ✅ Low ownership players displayed

---

## Common Issues & Solutions

### Issue: Backend won't start
```
Error: ModuleNotFoundError: No module named 'flask'
```
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Frontend won't compile
```
Error: Cannot find module 'react'
```
**Solution:**
```bash
cd frontend
rm -rf node_modules
npm install
npm start
```

### Issue: API 404 errors in browser console
```
GET http://localhost:5000/api/team/123/summary 404
```
**Solution:**
- Confirm backend is running: `python run.py`
- Check backend is on port 5000
- Check Team ID is valid FPL ID

### Issue: Slow loading (>5 seconds)
**Cause:** FPL API slowness or first-time bootstrap cache
**Solution:** Wait longer, subsequent requests faster

### Issue: "Failed to fetch team" error
**Solutions:**
1. Check Team ID is correct (should be 6+ digits)
2. Verify internet connection
3. Confirm FPL API is not down
4. Try different team ID as test

---

## Test Data

### Recommended Test Team IDs
- `1` - Official FPL test team
- `1065` - Widely known public team
- Use your own team ID for real testing

### What to look for

**Good test team indicators:**
- Multiple gameweeks played (shows history)
- Mix of expensive and cheap players
- Several differentials in squad
- Recent transfers visible

---

## Performance Testing

### Benchmark Times
- **Team Summary:** <1 second
- **Squad Overview:** 2-3 seconds
- **Smart Swaps:** 3-4 seconds
- **Transfers:** 3-4 seconds
- **Differentials:** 3-4 seconds

### If slower:
1. Check internet speed
2. Monitor API response times
3. Consider adding request caching
4. Look for n+1 API calls in browser Network tab

---

## Data Validation

### Verify Correct Data

**Squad Tab:**
- Total price = sum of all player prices
- Form = average of all player forms
- No missing players

**Transfers Tab:**
- All 5 positions represented
- Scores between 0-10
- Prices within reasonable range (£3-15m)

**Smart Swaps:**
- Replacements affordable
- Same position as removed player
- Improved form/value

**Differentials:**
- Ownership <15%
- Form >3.0
- All different players

---

## Browser Console Check

### No errors should appear:
```
❌ CORS errors
❌ 404 Not Found
❌ Undefined values
❌ Type errors
```

### If you see errors:
1. Copy full error message
2. Check backend logs
3. Restart both services

---

## API Testing (Curl / Postman)

### Test an endpoint directly

```bash
# Get current gameweek
curl http://localhost:5000/api/team/current-gameweek

# Get team summary
curl http://localhost:5000/api/team/1/summary

# Get squad overview
curl http://localhost:5000/api/team/1/squad-overview

# Get smart swaps
curl http://localhost:5000/api/team/1/smart-swaps

# Get transfers
curl http://localhost:5000/api/recommendations/1/transfers

# Get differentials
curl http://localhost:5000/api/recommendations/1/differentials
```

### Expected responses:
- Status 200 OK
- Valid JSON
- Expected fields present

---

## Regression Testing Checklist

- [ ] App starts without errors
- [ ] Team lookup works with multiple IDs
- [ ] All 5 tabs load
- [ ] Overview tab shows correct stats
- [ ] Squad tab displays all players
- [ ] Smart Swaps suggests underperformers
- [ ] Transfers shows top 5 per position
- [ ] Differentials identifies low ownership
- [ ] No console errors
- [ ] Responsive on mobile view
- [ ] Data loads within 5 seconds
- [ ] Prices match FPL API

---

## Known Limitations

1. **No real-time updates** - Refresh page to get latest
2. **No authentication** - Anyone can analyze any public team
3. **API rate limiting** - Very heavy usage may throttle (rare)
4. **Cached bootstrap data** - Updates on app restart
5. **No injury tracking** - See FPL site for injury info

---

## Debugging Tips

### View Backend Logs
```bash
# Terminal with backend running shows:
# - API requests
# - Response times
# - Any errors
```

### View Network Traffic
1. Open DevTools (F12)
2. Go to Network tab
3. Reload page
4. Check API response times
5. Verify JSON structure

### Check State
1. Open DevTools
2. Go to React tab (if installed)
3. Select component
4. View props and state
5. Verify data structure

---

## Success Criteria

Your app is working correctly when:

✅ **Functionality:**
- All 5 tabs load without errors
- Data displays immediately
- Transfers and differentials update correctly

✅ **Performance:**
- Initial load <2 seconds
- Tab switch <1 second
- No console errors

✅ **Data Quality:**
- Numbers make sense
- Players are real FPL players
- Prices match FPL site
- Form between 0-10
- Ownership between 0-100%

✅ **UX:**
- Buttons responsive
- Colors visible
- Text readable
- Mobile-friendly layout
- Clear error messages

---

**Ready to test? Start with [FEATURES_GUIDE.md](FEATURES_GUIDE.md) for full feature overview!**
