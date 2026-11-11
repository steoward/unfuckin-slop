---
id: imp.performance
title: UI performance — the design constraint that shows
triggers: performance, cls, layout shift, lcp, inp, font loading, images, lazy, jank, bundle, blur cost, optimize
pulls: apple.motion-a11y
weight: 6
---

# Performance as design

A layout that shifts is a design that lied about its measurements.

- **Reserve space for everything that loads:** images with `width`/`height` or `aspect-ratio`, embeds, ads, late fonts. CLS comes from un-reserved boxes, not from slow networks.
- **Fonts:** self-host, subset, `font-display: swap`, and preload the one face used above the fold. Match the fallback's metrics so the swap does not reflow.
- **Images:** `srcset`/`sizes`, AVIF or WebP, lazy-load below the fold, never lazy-load the hero, and never ship a 3000px file into a 400px slot.
- **Animation:** `transform`/`opacity` only. `backdrop-filter` on large or moving areas is the most common jank source in "premium" pages; cap the area and keep it static.
- **Measure the field metrics:** LCP, INP, CLS. Lab scores are a proxy, not the result.
- **JS budget:** if the interaction can be CSS, it should be. A 200KB animation library to fade in three sections is a design failure disguised as engineering.
- **`will-change` is a hint, not a fix.** Apply before motion, remove after; leaving it on many elements costs memory and can force layers.
