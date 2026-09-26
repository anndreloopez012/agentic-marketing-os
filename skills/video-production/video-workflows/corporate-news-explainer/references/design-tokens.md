# Design Tokens & Visual Language for Corporate News Explainers

This guide establishes the visual grammar for high-end corporate tech and financial explainers, inspired by premier fintech editorial infographics.

## 1. Color Palette

### Backgrounds
- **Deep Slate Canvas:** `#070d18` to `#0b1426` (never flat black `#000000`; use deep navy-slate).
- **Radial Hero Glow:** `radial-gradient(circle at 50% 15%, #172554 0%, #070d18 75%)`.
- **Engineering Grid:** `linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px)` with `60px 60px` sizing.

### Accent Roles
- **Primary Hook / Focus:** Cyan / Electric Blue (`#38bdf8`, `rgb(56, 189, 248)`)
- **Infrastructure / Processing:** Indigo / Violet (`#818cf8`, `#a855f7`)
- **Success & Approvals:** Emerald Mint (`#22c55e`, `#4ade80`)
- **Rejection & Risk:** Coral Crimson (`#ef4444`, `#f87171`)
- **Backend / Settlement / Time Delay:** Warm Amber / Gold (`#f59e0b`, `#fbbf24`)
- **Muted Supporting Text:** Slate 400 (`#94a3b8`) and Slate 300 (`#cbd5e1`)

## 2. Card Architecture (Glassmorphic Engineering)

```css
.explainer-card {
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 20px;
  padding: 24px 28px;
  backdrop-filter: blur(16px);
  position: relative;
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
}

/* Stage-specific glowing borders */
.explainer-card.is-active {
  border-color: #38bdf8;
  box-shadow: 0 0 40px rgba(56, 189, 248, 0.25);
}
```

## 3. Typography & Hierarchy

- **Title Font:** Clean, modern grotesque or geometric sans (`Inter`, `Plus Jakarta Sans`, system-ui).
- **Accent Note Font:** Casual script or editorial serif (`Caveat`, `Georgia`, or italic styled cursive) for humanized corner notes (e.g. *"Una compra. Muchas piezas. Todo en segundos."*).
- **Step Badges:** Circular numbered pills (`width: 44px; height: 44px; border-radius: 50%; border: 2px solid; font-weight: 800`).

## 4. Connector Geometry

- **Forward Pipeline Arrows:** Horizontal SVG paths between cards with `marker-end="url(#arrow)"`.
- **Return Loop:** Dotted curved line below the cards with `stroke-dasharray="8 6"` traveling from the final decision back to the user/POS.
