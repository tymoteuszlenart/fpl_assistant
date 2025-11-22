# Visual Design Reference

## Design Inspiration

The FPL Assistant UI combines modern design principles with sports analytics best practices:

- **Enterprise SaaS aesthetic**: Clean, professional, trustworthy
- **Data visualization focus**: Information hierarchy, clear patterns
- **Modern web standards**: Gradient backgrounds, smooth animations, responsive layouts
- **Sports dashboard feel**: Bold stats, clear performance indicators, player focus

## Key Design Elements

### 1. Gradient Backgrounds

Primary gradient (used throughout):
```
#667eea → #764ba2
(Light purple to darker purple)
```

This creates:
- Professional, modern appearance
- Good contrast with white text
- Calming, trustworthy feeling
- Consistent visual identity

Light gradient (card backgrounds):
```
#f8f9fa → #ede7f6
(Almost white to very light purple)
```

This creates:
- Subtle depth without being harsh
- Better visual separation from white
- Soft, refined appearance
- Easy to read dark text

### 2. Shadows & Elevation

Shadow hierarchy:
```css
/* Small elevation (4px) */
box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);

/* Medium elevation (8px) */
box-shadow: 0 8px 20px rgba(102, 126, 234, 0.2);

/* Large elevation (12px) */
box-shadow: 0 12px 35px rgba(102, 126, 234, 0.3);
```

Creates sense of depth without being overdone.

### 3. Border Radius

Radius hierarchy:
```css
Small: 6px      (for tiny badges)
Medium: 10px    (for normal buttons)
Large: 14px     (for main cards)
Extra: 16px     (for container)
```

Modern, friendly appearance while staying professional.

### 4. Color Accents by Position

```
GK  (Goalkeeper)    → Primary purple
DEF (Defender)      → Primary purple
MID (Midfielder)    → Primary purple
FWD (Forward)       → Primary purple

Status Colors:
Excellent   → Green (#28a745)
Good        → Blue (#667eea)
Average     → Amber (#ffc107)
Poor        → Red (#d32f2f)
```

### 5. Typography System

**Headings**:
- Main title (H1): 36px, bold, purple color
- Section titles (H2): 18px, bold, purple color
- Card titles (H3): 16px, bold, dark gray
- Subsections (H4): 15px, semi-bold, purple color

**Body**:
- Large text: 16px, 5:1 contrast
- Normal text: 14px, 4.5:1 contrast
- Small text: 12px, 4.5:1 contrast
- Tiny text: 11px, 4.5:1 contrast

All with proper letter-spacing and line-height.

### 6. Spacing System

**Macro spacing** (between major sections):
```
40-50px between main sections
30-35px between subsections
```

**Micro spacing** (within components):
```
20-25px padding in cards
12-18px margin between items
6-10px tight spacing
```

Creates professional, airy feel without looking sparse.

## Component Design Showcase

### Stats Grid
```
┌─────────────────────────────────────────────┐
│  ┌─────────┬─────────┬─────────┬─────────┐  │
│  │ Stat 1  │ Stat 2  │ Stat 3  │ Stat 4  │  │
│  │ 12,345  │    5    │   GW20  │    3    │  │
│  └─────────┴─────────┴─────────┴─────────┘  │
│  Gradient background, shadows, hover lift   │
└─────────────────────────────────────────────┘
```

### Position Card (Transfers)
```
┌──────────────────────────────┐
│ GK (Purple gradient header)   │  ← White text
├──────────────────────────────┤
│ ┌──────────────────────────┐  │
│ │ Player Name    Score: 8.2│  │  ← Light gradient bg
│ │ Team | £5.0m | Form: 4   │  │  ← Color-coded badges
│ │ 15.5% owned              │  │
│ │ "Best form this season"  │  │  ← Italic reason
│ └──────────────────────────┘  │
│ ┌──────────────────────────┐  │
│ │ (more players...)        │  │
│ └──────────────────────────┘  │
└──────────────────────────────┘
```

### Squad Player Card
```
┌────────────────────┐
│ [Player Photo]     │  ← 80x100px, rounded
│ (80x100px)         │
├────────────────────┤
│ Player Name        │  ← Bold, 14px
│ Manchester City    │  ← Team, purple
│ £8.5m              │  ← Green
│ Form: 6            │  ← Gray
│ 2.15 pts/£m        │  ← Purple, bold
│ ┌────────────────┐ │
│ │     GOOD       │ │  ← Performance badge
│ └────────────────┘ │
└────────────────────┘
 ↑ Top border: color-coded (green for good)
```

### Smart Swap Card
```
┌────────────────────────────────────────────┐
│                                            │
│  REMOVE:           ⟶          ADD:         │
│  Poor Player                  Good Player  │
│  [Photo]                       [Photo]     │
│  £6.0m | Injured               Player B    │
│  "Player injured"              £7.5m       │
│                                "Great form"│
│                                            │
│                  (Multiple options below)  │
└────────────────────────────────────────────┘
```

### Differential Card
```
┌──────────────────────────────┐
│ [Player Photo]               │  ← Full width
│ (200px height)               │
├──────────────────────────────┤
│ Player Name        Score 7.1 │  ← White text
│ ManCity | £5.0m | Form: 5    │
│ 3.2% owned (Low ownership!)  │  ← Red accent
│ "Underrated gem this week"   │
└──────────────────────────────┘
 ↑ Purple gradient background
```

## Animation Patterns

### Hover Effects

**Cards (lift up)**:
```
transform: translateY(-6px)
shadow: increase to next level
transition: 0.3s ease-in-out
```

**List Items (slide right)**:
```
transform: translateX(4px)
shadow: increase slightly
transition: 0.3s ease-in-out
```

**Buttons (color shift)**:
```
color: change to primary
transition: 0.3s ease
no transform (feels snappier)
```

### Tab Transitions

When switching tabs:
```
content: fade-in animation
opacity: 0 → 1
transform: translateY(10px) → translateY(0)
duration: 0.3s
```

Creates smooth, professional tab switches.

## Responsive Design Flow

### Desktop (> 1200px)
```
Stats: 5 columns
Positions: 4 columns  
Squads: 4 players per position
Padding: 40px
```

### Tablet (768-1200px)
```
Stats: 3 columns
Positions: 2 columns
Squads: 3 players per position
Padding: 30px
```

### Mobile (480-768px)
```
Stats: 2 columns
Positions: 1 column
Squads: 1 column
Padding: 20px
Tabs: scroll horizontally
```

### Small Mobile (< 480px)
```
Everything: 1 column
Stats: stacked
Padding: 15px
Minimal gaps: 10px
```

## Accessibility Considerations

### Color Contrast
- Text on colored background: 4.5:1 or higher
- All text readable by colorblind users
- Status indicated by position, not just color

### Touch Targets
- Minimum 44px on mobile devices
- Tabs, buttons properly spaced
- No tiny click targets

### Focus States
- All interactive elements have visible focus
- Focus visible with outline or background change
- Keyboard navigation fully supported

### Motion
- No excessive animations
- Respects `prefers-reduced-motion` preference
- Important interactions don't rely on animation

## Brand Guidelines

### Primary Color
- **Hex**: #667eea (Main)
- **Hex**: #764ba2 (Complement)
- **Usage**: Headers, highlights, active states, brand identity

### Secondary Colors
- **Success**: #28a745 (Green)
- **Warning**: #ffc107 (Amber)
- **Error**: #d32f2f (Red)
- **Info**: #1976d2 (Blue)

### Neutral Colors
- **Dark Text**: #1a1a1a (Almost black)
- **Medium Text**: #333 (Dark gray)
- **Light Text**: #666 (Medium gray)
- **Hint Text**: #999 (Light gray)
- **Borders**: #ccc, #e0e0e0

### Fonts
- **Font Stack**: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif
- **Weights Used**: 400 (regular), 500 (medium), 600 (semi-bold), 700 (bold)

## CSS Architecture

### File Structure
```
TeamAnalysis.css (~600 lines)
├── Global styles
├── Layout (team-analysis container)
├── Typography & headers
├── Stats grid
├── Tabs & navigation
├── Transfers section
├── Differentials section
├── Squad section
├── Smart swaps section
├── Responsive breakpoints
└── Animations & transitions
```

### Key Classes
```
.team-analysis          Main container
.team-header            Title section
.stats-grid             5 stat cards
.tabs                   Tab navigation
.positions-grid         Transfers/diffs layout
.position-card          Individual position card
.player-item            Player in card
.squad-player           Squad member card
.swap-card              Smart swap suggestion
.differential-item      Differential player
```

## Future Enhancements

1. **Dark Mode**: Toggle between light/dark themes
2. **Custom Themes**: Allow user color customization
3. **Advanced Animations**: Use Framer Motion for complex transitions
4. **Loading States**: Skeleton screens for better UX
5. **Print Styles**: Professional printable reports
6. **SVG Icons**: Replace some text with icons
7. **Micro-interactions**: Advanced hover states, ripple effects
8. **Data Visualization**: Charts, graphs for metrics

## Common UI Patterns

### Success State
```
Background: Light green (#e8f5e9)
Border: Green (#28a745)
Text: Dark gray
Icon: Green checkmark
```

### Error State
```
Background: Light red (#ffebee)
Border: Red (#d32f2f)
Text: Dark gray
Icon: Red exclamation
```

### Loading State
```
Background: Light blue (#f3f4ff)
Border: Purple (#667eea)
Animation: Subtle pulse or shimmer
```

### Empty State
```
Background: Light gray (#f9f9f9)
Text: Medium gray (#999)
Icon: Outline style
Message: Helpful and actionable
```

---

This design system provides a solid foundation for scaling the FPL Assistant UI while maintaining consistency and professional quality.
