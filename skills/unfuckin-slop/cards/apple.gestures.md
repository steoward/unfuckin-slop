---
id: apple.gestures
title: Gesture design — hysteresis, parallel recognition, sane taps
triggers: tap, double tap, gesture, hysteresis, threshold, swipe, drag, recognizer, hit area, cancel, touch target
pulls: apple.direct-manipulation, apple.velocity-projection
weight: 6
---

# Gesture details

- **Tap:** highlight on touch-*down* (instant), commit on touch-*up*. Allow cancel-by-dragging-away and back. Add ~10px of hit padding around the visual target.
- **Drag/swipe:** require a small movement threshold (~10px) before committing to an axis, then track 1:1. Without hysteresis, a slightly shaky press reads as a drag.
- **Detect all plausible gestures in parallel from the first move**, then confidently cancel the losers once intent is clear. Choose the axis with the larger early delta and stick with it.
- **Avoid recognizers that only report a final state** (`swipeleft`-style). They throw away the continuous tracking that feedback and velocity need.
- **Minimise disambiguation delays.** Double-tap detection unavoidably delays single taps; pay that cost only where double-tap truly exists.

# Hit areas

A 12px icon still needs a ~44px target on touch. Grow the hit area with padding or a pseudo-element, not by drawing a bigger icon.

# Smell test

If a gesture has no visible affordance and no alternative control, it is a secret, and secrets are not design. If disabling JavaScript leaves nothing operable, the gesture was decoration.
