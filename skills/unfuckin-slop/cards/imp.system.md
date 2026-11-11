---
id: imp.system
title: Design system — tokens, and a DESIGN.md worth reading
triggers: design system, tokens, design.md, css variables, component library, consistency, extract, document, theme
pulls: imp.typeset, imp.color
weight: 6
---

# Tokens

Name tokens for their role, not their value: `--surface-raised`, `--text-muted`, `--border-subtle`, `--focus-ring`, `--space-3`, `--radius-md`, `--ease-out`. A token called `--blue-500` is a colour, not a decision.

- One source of truth: CSS custom properties, exported to any platform that needs them.
- Components consume tokens only. A raw hex in a component is a bug.
- Two tiers at most: primitives (palette, scale) and semantic (surface, text, border). A third tier is usually a naming failure.
- Every token must be used. Unused tokens are speculation, and they rot.

# DESIGN.md

Keep it under ~60 lines and make it operational:

```md
# <Product> design system
World: <one sentence: the material, era, and mood>
Mode: Persuade | Operate | Read | Experience
Type: <family>, scale <ratio>, tracking <rule>
Colour: <dominant hue>, <neutral tint>, <accent>, dark mode <rule>
Space: <base unit>; radius <scale>
Motion: <easing>, <durations>, <the one authored moment>
Do: <3 bullets>
Don't: <3 bullets, referencing the bans>
```

If a section cannot be filled without guessing, the design is not a system yet. Extract from the code that exists, do not invent forward-looking rules the code does not follow.
