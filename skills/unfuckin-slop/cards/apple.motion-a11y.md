---
id: apple.motion-a11y
title: Motion accessibility and frame-level smoothness
triggers: reduced motion, accessibility, vestibular, prefers-reduced-motion, transparency, contrast, smoothness, jank, frame rate, will-change, motion blur
pulls: apple.materials, imp.a11y
weight: 7
---

# Reduced motion

Reduced motion does not mean no feedback. It means a gentler, non-vestibular equivalent.

- `prefers-reduced-motion: reduce` → replace slides, springs, and parallax with short opacity cross-fades or static transitions. Drop elastic overshoot. Keep opacity and colour changes that aid comprehension.
- `prefers-reduced-transparency: reduce` → make surfaces frostier or solid: raise background opacity, drop the blur.
- `prefers-contrast: more` → near-solid backgrounds with a defined contrasting border.

```css
@media (prefers-reduced-motion: reduce) {
  .sheet { transition: opacity 200ms ease; transform: none !important; }
}
@media (prefers-reduced-transparency: reduce) {
  .toolbar { background: white; backdrop-filter: none; }
}
```

Also avoid full-viewport moving backgrounds, slow looping oscillations near 0.2 Hz (one cycle per 5s), and abrupt brightness jumps (ease theme changes). Make large moving objects semi-transparent while they travel; fade big surfaces out during a large reposition and back in once settled.

# Frame smoothness

Smoothness is about what is in the frames, not only the frame rate.

- Keep per-frame positional change below the perception threshold to avoid strobing.
- For very fast motion, a subtle motion blur or stretch encodes speed and reads better than a hard sharp streak.
- `requestAnimationFrame` is the web's display-synced clock (Apple uses `CADisplayLink`). Animate compositor-friendly properties only: `transform` and `opacity`. Hint `will-change` only where motion is imminent, and remove it after.
