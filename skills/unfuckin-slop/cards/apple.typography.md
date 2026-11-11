---
id: apple.typography
title: Typography — optical sizing, size-specific tracking, inverse leading
triggers: typography, font, tracking, letter-spacing, leading, line-height, optical size, dynamic type, type scale, heading, body, measure
pulls: imp.typeset
weight: 8
---

# Typography

Apple designs type to change shape with size; the same discipline applies on the web.

- **Tracking is size-specific — never one value for all sizes.** Large display text wants negative tracking (letters read too far apart as they grow); small text wants slightly positive tracking. A fixed `letter-spacing` is wrong somewhere. Tighten headings, leave body near `0`.
- **Leading tracks size inversely.** Tight on large headings, looser on body. Increase it for scripts with tall ascenders/descenders; tighten it for dense, information-heavy UI.
- **Build hierarchy from weight + size + leading as a set**, not size alone. Weight adds presence without taking space.
- **Respect the user's text-size setting.** Scale layout with the text: spacing in `rem`/`em`, not fixed px, so larger type does not break the layout.
- **Default to the platform's system font** before a custom face. It ships optical sizing, tracking tables, and legibility tuning. Override only with a reason.

```css
:root { font: 100%/1.5 system-ui, sans-serif; }

.display {
  font-size: clamp(2rem, 5vw, 4rem);
  line-height: 1.05;       /* tight leading for large text */
  letter-spacing: -0.02em; /* negative tracking as it grows */
  font-optical-sizing: auto;
}
```

# Floors

- Body measure 65–75ch; display capped around 6rem.
- Tracking floor -0.04em. Tighter and letters touch: cramped, not designed.
- Body and placeholder contrast ≥4.5:1, large text ≥3:1.
- Tabular numerals for any column of numbers that should align.
