# UI Styling Guide

## Overview

The FPL Assistant frontend has been completely redesigned with a modern, professional aesthetic featuring:

- **Clean gradient backgrounds** with smooth transitions
- **Elevated card designs** with subtle shadows
- **Consistent color palette** (primary: #667eea, secondary: #764ba2)
- **Responsive typography** with proper hierarchy
- **Smooth animations** and hover effects
- **Mobile-first responsive design**

## Design System

### Color Palette

| Purpose | Color | Hex Code | Usage |
|---------|-------|----------|-------|
| Primary | Purple Gradient | #667eea → #764ba2 | Headers, highlights, active states |
| Success | Green | #28a745 | Positive metrics, excellent performance |
| Warning | Amber | #ffc107 | Average performance, caution states |
| Danger | Red | #d32f2f | Poor performance, errors |
| Info | Blue | #1976d2 | Information badges |
| Neutral | Gray | #666, #999, #ccc | Text, borders, backgrounds |

### Typography

```
Headings:
  H1 (Team Name): 36px, weight 700, letter-spacing -0.5px
  H2 (Position Title): 18px, weight 700, letter-spacing 0.5px
  H3 (Card Headers): 16px, weight 700
  H4 (Section Headers): 15px, weight 600

Body Text:
  Large: 16px, weight 500
  Normal: 14px, weight 400
  Small: 12px, weight 400
  Tiny: 11px, weight 400
```

### Spacing

```
Margins:
  XL: 40-50px  (major sections)
  LG: 30-35px  (section breaks)
  MD: 20-25px  (component spacing)
  SM: 12-18px  (internal spacing)
  XS: 6-10px   (tight spacing)

Padding:
  Cards: 16-20px
  Headers: 15-18px
  Sections: 20-30px
```

## Component Styling

### Stats Grid

**Desktop (5 columns)**: Each stat card spans full height
**Tablet (2-3 columns)**: Wraps dynamically
**Mobile (1 column)**: Stack vertically

```css
.stat-card {
  Gradient: #667eea → #764ba2
  Shadow: 0 8px 25px rgba(102, 126, 234, 0.2)
  Hover: Lift up 6px, shadow increase
  Padding: 28px 20px
  Border-radius: 14px
}
```

### Position Cards (Transfers/Differentials)

**Desktop**: 2-4 cards per row
**Tablet**: 2 cards per row
**Mobile**: 1 card per row

```css
.position-card {
  Header: Linear gradient (purple), white text
  Body: Light gradient background (#f9f9f9 → #f0f2ff)
  Border: 2px solid #e0e0e0
  Hover: Border turns purple, shadow increases
  Border-radius: 14px
}
```

### Player Items

```css
.player-item {
  Background: Light gradient
  Left border: 4px solid #667eea (accent)
  Hover effects:
    - Lift up 6px
    - Shadow increase
    - Background darkens
    - Slight rightward translation
}
```

### Squad Players

```css
.squad-player {
  Background: White
  Top border: 4px colored (status-dependent)
  Excellent: #28a745 (green)
  Good: #667eea (purple)
  Average: #ffc107 (amber)
  Poor: #dc3545 (red)
  
  Hover: Lift 8px, shadow increase
  Image: 80x100px, rounded corners
}
```

### Smart Swaps

```css
.swap-card {
  Layout: Flex, space-between
  "Remove" section: Red accent, left side
  Arrow: Large purple →
  "Add" section: Green accents, right side
  Individual swaps: Green gradient background
  
  Hover: Border highlights, background darkens
  Mobile: Stacks vertically, arrow centered
}
```

### Differentials

```css
.differential-item {
  Background: Purple gradient (#667eea → #764ba2)
  Image: Top, 200px height, full width
  Content: White text on purple
  Hover: Lift 8px, shadow increase
  
  Details: Semi-transparent white badges
  Score: Prominent, larger font
}
```

### Tabs

```css
.tab-button {
  Inactive: Gray text, transparent background
  Hover: Text turns purple
  Active: Purple text, 4px purple bottom border
  
  Smooth transition: 0.3s all
  Responsive: Wrap on mobile, scroll on small screens
}
```

## Animations

### Standard Transitions
- **Duration**: 0.3s
- **Timing**: ease-in-out
- **Properties**: transform, box-shadow, background, color

### Hover Effects

**Cards**:
```css
.card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.15);
}
```

**List Items**:
```css
.item:hover {
  transform: translateX(4px);
  box-shadow: 0 6px 18px rgba(102, 126, 234, 0.2);
}
```

**Player Photos**:
```css
.player-photo:hover {
  Subtle zoom effect on parent
}
```

## Responsive Breakpoints

### Desktop (> 1200px)
- 4-column grids for transfers
- 2x2 or 4x1 squad layouts
- Full padding (40px)
- Large fonts and spacing

### Tablet (768px - 1200px)
- 2-column grids
- Medium padding (30px)
- Adjusted font sizes

### Mobile (< 768px)
- 1-column layout
- Reduced padding (20px)
- Smaller fonts
- Wrapped tabs
- Stacked swap cards

### Small Mobile (< 480px)
- Minimal padding (15px)
- Very small fonts (11-12px)
- Tighter spacing
- Single column everything

## Accessibility

### Color Contrast
- Primary text on white: 4.5:1+ contrast
- Labels on colored backgrounds: 4.5:1+ contrast
- Ensures WCAG AA compliance

### Interactive Elements
- Minimum 44px tap targets on mobile
- Hover states clearly visible
- Focus states for keyboard navigation
- Alt text on all images

### Responsive Typography
- Readable at all breakpoints
- Proper line-height: 1.4-1.8
- Letter-spacing for headings: -0.5px to 0.5px

## Common Patterns

### Section Header
```tsx
<div className="position-group">
  <h4>Position Name</h4>
  <div className="players-grid">
    {/* Players */}
  </div>
</div>
```

### Player Card
```tsx
<div className="player-item">
  {image && <img src={image} alt={name} />}
  <div className="player-header">
    <span className="player-name">{name}</span>
    <span className="player-score">{score}</span>
  </div>
  <div className="player-details">
    <span className="badge">{team}</span>
    <span className="price">£{price}m</span>
    <span className="form">Form: {form}</span>
    <span className="ownership">{owned}%</span>
  </div>
  <p className="reason">{reason}</p>
</div>
```

### Stat Card
```tsx
<div className="stat-card">
  <div className="stat-label">METRIC NAME</div>
  <div className="stat-value">VALUE</div>
</div>
```

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile browsers: iOS Safari 12+, Chrome for Android

## Performance Optimization

### CSS Features Used
- CSS Grid and Flexbox (no float)
- CSS custom properties where applicable
- Minimal media queries
- Hardware-accelerated transforms

### Image Optimization
- Player photos: WebP where available
- Size: 60x60px for lists, 80x100px for squad
- Lazy loading via browser native loading="lazy"

### Best Practices
- Single CSS file: ~500 lines
- No CSS-in-JS overhead
- Critical styles loaded first
- Animations use GPU-accelerated properties (transform, opacity)

## Customization

### Changing Primary Color
To change the primary color from purple (#667eea) to another color:

1. Find all instances of `#667eea`
2. Replace with your hex code
3. Update the companion gradient color `#764ba2` to a complementary shade

### Adjusting Spacing
Modify the margin/padding values in spacing variables:
```css
--spacing-xs: 8px;
--spacing-sm: 12px;
--spacing-md: 20px;
--spacing-lg: 30px;
--spacing-xl: 40px;
```

### Dark Mode (Future)
Currently not implemented, but the design is prepared for:
- CSS custom properties for colors
- Media query `prefers-color-scheme: dark`
- Sufficient contrast ratios for both modes

## Testing Checklist

- [ ] Desktop (1920px+): All elements aligned, proper spacing
- [ ] Tablet (768px-1024px): 2-column grids working
- [ ] Mobile (375px-767px): 1-column layout, tabs wrapping
- [ ] Small Mobile (< 375px): All text readable, buttons tappable
- [ ] Touch devices: Hover effects work on all platforms
- [ ] Slow networks: Critical content loads first
- [ ] High contrast mode: All elements distinguishable
- [ ] Keyboard navigation: All interactive elements reachable

## Known Limitations

1. **CSS Grid Support**: Requires modern browser (IE not supported)
2. **CSS Gradients**: Some older devices may show solid colors
3. **Transform Support**: Required for smooth animations
4. **Flex Wrap**: May require adjustment on very narrow screens
5. **SVG Support**: For future icon enhancements

## Future Enhancements

- [ ] Dark mode support
- [ ] Theme customization UI
- [ ] Advanced animations (Framer Motion)
- [ ] Improved accessibility (ARIA labels)
- [ ] Print-friendly styling
- [ ] SVG icons
- [ ] WebP image format support
