# FPL Assistant - UI Guide

## Visual Layout

### Main Screen
```
┌─────────────────────────────────────────────┐
│         🏆 FPL Assistant 🏆                 │
│   Fantasy Premier League Transfer Recs      │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│                Team Search                   │
│  ┌──────────────────────────────────────┐   │
│  │ Enter Team ID: [123456        ]      │   │
│  │                    [Analyze Team]    │   │
│  └──────────────────────────────────────┘   │
│  "Enter your FPL Team ID to get recs"      │
└─────────────────────────────────────────────┘

AFTER ANALYSIS:

┌─────────────────────────────────────────────┐
│         My FPL Team                         │
│         Manager: John Doe                   │
├─────────────────────────────────────────────┤
│  Total Points: 850    Overall Rank: 50,000 │
│  Current GW: 15       Transfers Left: 1    │
│  Transfer Bank: £2.5m                      │
├─────────────────────────────────────────────┤
│  [Overview] [Best Transfers] [Differentials]│
├─────────────────────────────────────────────┤
│                                             │
│  TAB CONTENT SHOWS HERE                     │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Tab 1: Overview

```
┌─────────────────────────────────────────────┐
│ [Overview]  Best Transfers  Differentials   │
├─────────────────────────────────────────────┤
│                                             │
│  ✓ Team Summary displayed above              │
│  ✓ All key stats visible                    │
│                                             │
│  "Select 'Best Transfers' to see            │
│   optimized transfer recommendations        │
│   per position."                            │
│                                             │
│  "Select 'Differentials' to discover        │
│   low-ownership players with high           │
│   potential."                               │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Tab 2: Best Transfers

```
┌─────────────────────────────────────────────┐
│  Overview  [Best Transfers]  Differentials  │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────────┐ ┌─────────────────┐  │
│  │  GK (Goalies)    │ │  DEF            │  │
│  ├──────────────────┤ ├─────────────────┤  │
│  │ • Ederson        │ │ • VVD           │  │
│  │   MCI • £5.5m    │ │   LIV • £6.5m   │  │
│  │   Form: 6.2      │ │   Form: 5.8     │  │
│  │   45% owned      │ │   52% owned     │  │
│  │   Expected: 6.5  │ │   Expected: 5.2 │  │
│  │   FDR: 2.5       │ │   FDR: 2.3      │  │
│  │   Score: [6.2]   │ │   Score: [5.9]  │  │
│  │   "Excellent..." │ │   "Good form..."│  │
│  │                  │ │                 │  │
│  │ • Ramsdale       │ │ • Dias          │  │
│  │   ARS • £5.0m    │ │   MCI • £5.8m   │  │
│  │   ...            │ │   ...           │  │
│  │                  │ │                 │  │
│  │ • Lloris         │ │ • Shaw          │  │
│  │   TOT • £5.5m    │ │   MUN • £4.5m   │  │
│  │   ...            │ │   ...           │  │
│  └──────────────────┘ └─────────────────┘  │
│                                             │
│  ┌──────────────────┐ ┌─────────────────┐  │
│  │  MID             │ │  FWD            │  │
│  ├──────────────────┤ ├─────────────────┤  │
│  │ • De Bruyne      │ │ • Haaland       │  │
│  │   MCI • £11.5m   │ │   MCI • £11.8m  │  │
│  │   Form: 7.1      │ │   Form: 7.4     │  │
│  │   68% owned      │ │   78% owned     │  │
│  │   Expected: 8.2  │ │   Expected: 9.1 │  │
│  │   FDR: 2.3       │ │   FDR: 2.2      │  │
│  │   Score: [7.3]   │ │   Score: [8.1]  │  │
│  │   "Outstanding.."│ │   "Premium...   │  │
│  │                  │ │                 │  │
│  │ • Saka           │ │ • Alvarez       │  │
│  │   ARS • £8.0m    │ │   MCI • £8.5m   │  │
│  │   ...            │ │   ...           │  │
│  │                  │ │                 │  │
│  │ • Rashford       │ │ • Toney         │  │
│  │   MUN • £6.5m    │ │   BRE • £7.0m   │  │
│  │   ...            │ │   ...           │  │
│  └──────────────────┘ └─────────────────┘  │
│                                             │
└─────────────────────────────────────────────┘

Key Colors:
- Team Badge: Light Blue (#e3f2fd)
- Price: Green (#2e7d32)
- Form: Orange (#f57c00)
- Ownership: Purple (#7b1fa2)
- Score: Purple Gradient Badge
```

---

## Tab 3: Differentials

```
┌─────────────────────────────────────────────┐
│  Overview  Best Transfers  [Differentials]  │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────────────────────────┐      │
│  │ Brennan Johnson  FWD     [7.1]   │◄─ Score
│  │ NOT • £7.0m  Form: 5.5           │
│  │ 8.2% owned ⭐ Expected: 5.8      │
│  │ "Low ownership with form 5.5"    │
│  │ "Easy fixtures (FDR 2.8)"        │
│  └──────────────────────────────────┘
│       ▲ Highlighted as VERY LOW ownership
│
│  ┌──────────────────────────────────┐
│  │ Anthony Gordon  MID      [6.8]   │
│  │ EVE • £5.5m  Form: 4.9           │
│  │ 12.1% owned ⭐ Expected: 4.6     │
│  │ "Low ownership (12.1%)"           │
│  │ "Good form, easy fixtures"       │
│  └──────────────────────────────────┘
│
│  ┌──────────────────────────────────┐
│  │ Jordan Pickford  GK      [6.5]   │
│  │ EVE • £5.0m  Form: 5.2           │
│  │ 2.3% owned ⭐⭐⭐ Expected: 4.2   │
│  │ "Extremely low ownership!"       │
│  │ "Solid form, very unique pick"   │
│  └──────────────────────────────────┘
│
│  ┌──────────────────────────────────┐
│  │ Matheus Nunes  MID       [6.3]   │
│  │ WOL • £5.8m  Form: 4.7           │
│  │ 9.5% owned ⭐ Expected: 4.1      │
│  └──────────────────────────────────┘
│
│  ┌──────────────────────────────────┐
│  │ Richarlison  FWD         [6.1]   │
│  │ TOT • £7.2m  Form: 3.8           │
│  │ 5.7% owned ⭐⭐ Expected: 3.5     │
│  └──────────────────────────────────┘
│                                             │
└─────────────────────────────────────────────┘

Differential Card Design:
- Yellow/Gold background (#fff5e1 to #fff9c4)
- Gold border (#fbc02d)
- Orange position badge
- Red ownership % (⭐ highlights very low %)
- Shows differential score, not regular score
```

---

## Color Legend

```
Blue (#667eea)           - Primary, scores, active tabs
Purple (#764ba2)         - Gradient, premium
Yellow/Gold (#fbc02d)    - Differentials, highlights
Green (#2e7d32)          - Price, value
Orange (#f57c00)         - Form, position
Purple (#7b1fa2)         - Ownership
Red (#d32f2f)            - Low ownership (differential indicator)
Light Blue (#e3f2fd)     - Team badges
Light Gray (#f9f9f9)     - Card backgrounds
```

---

## Responsive Design

### Desktop (Full width)
```
Positions: 4 columns (GK, DEF, MID, FWD side by side)
Differentials: 3 columns (cards arranged horizontally)
Stats: 5 columns (all visible)
```

### Tablet (768px)
```
Positions: 2 columns (wrapping layout)
Differentials: 2 columns
Stats: 2 columns
```

### Mobile (< 768px)
```
Positions: 1 column (stacked)
Differentials: 1 column (full width)
Stats: 2 columns
Tabs: Scrollable, smaller buttons
```

---

## User Interactions

### Hover Effects
```
Player Cards (Transfers):
┌──────────────────┐
│ Player Name      │  ◄─ Slight elevation
│ Team • £5.0m     │     Box shadow added
│ Form: 6.2        │     Slight right shift
│ ...              │
└──────────────────┘

Differential Cards:
┌──────────────────────┐
│ Player Name          │  ◄─ Larger elevation
│ Team • £7.0m         │     More shadow
│ 8.2% owned           │     Slight upward shift
│ ...                  │
└──────────────────────┘
```

### Loading State
```
"Loading recommendations..."  [rotating spinner animation]

(Shows for 1-3 seconds while API fetches data)
```

### Error State
```
Error: Failed to fetch recommendations

(Red text, user can try again)
```

---

## Information Hierarchy

### What Catches Your Eye First
1. **Player Name** - Bold, large
2. **Team Badge** - Colored, recognizable
3. **Score** - Purple badge, top right (or Differential Score)
4. **Ownership %** - Red if very low
5. **Price** - Green, financial constraint
6. **Form** - Orange, recent performance
7. **Reason Text** - Smaller, italic explanation

### Reading Order (per card)
```
Name [Score]        ◄─ What & How good
Team • Price        ◄─ Who & Cost
Form | Ownership    ◄─ Performance & Uniqueness
"Reason text"       ◄─ Why
```

---

## Pro Tips for Using UI

1. **Quick Scan**
   - Highest scores first in each position
   - Differentials ordered by differential_score
   - Compare prices for value judgment

2. **Deep Analysis**
   - Read "reason" text for insights
   - Compare form across positions
   - Look for patterns (e.g., all defense low form)

3. **Decision Making**
   - Top 2-3 in each position = safest
   - Scroll for contrarian options
   - Mix top scorers with low-ownership picks

4. **Mobile Usage**
   - Stack saves space
   - Tap tabs to switch views
   - Screenshot for comparisons

---

**Layout designed for quick, informed decision-making! 🎯**
