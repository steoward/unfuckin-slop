---
id: imp.motion
title: Motion — one authored moment, exponential ease-out
triggers: animation, motion, transition, easing, cubic-bezier, entrance, hover, micro-interaction, stagger, page load
pulls: apple.springs, apple.motion-a11y
weight: 8
---

# Motion

- **One authored moment per view.** Pick the thing that should feel alive: the hero reveal, the sheet, the number. Everything else stays quiet. Identical fade-ups on every section are the motion equivalent of gray.
- **Exponential ease-out from an already-visible default.** `cubic-bezier(0.16, 1, 0.3, 1)`. Content must be readable before the animation starts and after it ends.
- **Durations:** 120–200ms for state changes, 200–320ms for surfaces, up to ~400ms for a large compositional move. Longer than that needs a reason.
- **Motion explains change.** It shows origin, relation, or causality: a menu grows from its trigger, a row expands from its summary, a route pushes from the direction of travel. Motion that only decorates is noise.
- **Stagger sparingly.** 20–40ms between related items, and only on first appearance. Never stagger a list the user will re-render.
- **Animate `transform` and `opacity`.** Layout properties cost frames and break interruptibility.
- **Respect `prefers-reduced-motion`** with a cross-fade, not a slower slide.
- **No `transition: all`.** It animates properties you did not intend and hides the ones you did.

```css
:root { --ease-out: cubic-bezier(0.16, 1, 0.3, 1); }
.reveal { opacity: 0; transform: translateY(8px); transition: opacity 240ms var(--ease-out), transform 240ms var(--ease-out); }
.reveal[data-shown] { opacity: 1; transform: none; }
@media (prefers-reduced-motion: reduce) { .reveal { transition: opacity 160ms linear; transform: none; } }
```
