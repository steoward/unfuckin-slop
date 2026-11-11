---
id: imp.color
title: Colour — one dominant hue, tinted neutrals, honest dark mode
triggers: color, colour, palette, accent, contrast, dark mode, neutral, tint, gradient, tokens, hue
pulls: imp.craft-floor, imp.a11y
weight: 8
---

# Colour

- **One dominant hue, one neutral ramp, one accent.** If every section has its own colour, the page has no identity.
- **Tint neutrals from the dominant hue** (2–8% saturation) instead of pure gray. Instant coherence for almost no work.
- **Do not use pure black or pure white** for large surfaces. `#0a0a0a` and `#fafafa` read as designed; `#000`/`#fff` read as default.
- **Dark mode is not an inversion.** Elevation goes *lighter* with height, shadows lose meaning and need borders or surface lightness, and saturated accents need desaturating to stay legible.
- **Contrast floors, always:** body ≥4.5:1, large text ≥3:1, UI boundaries and focus rings ≥3:1. Check the actual hex pairs.
- **On coloured surfaces, tint secondary text from that hue** or use the foreground at reduced opacity. Neutral gray on colour looks dirty.
- **Colour on a solid layer, not on translucent foreground.** Blur plus saturated text is a legibility trap.
- **Gradients need a reason.** A gradient that exists to make a flat area "interesting" is decoration. A gradient that models light, depth, or a material is design.
- **Semantic tokens, not raw hex, in components.** `--surface-raised`, `--text-muted`, `--focus-ring`. Renaming a palette should not require a component rewrite.
