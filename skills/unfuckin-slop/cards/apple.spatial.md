---
id: apple.spatial
title: Spatial consistency — symmetric paths, anchored origins, soft edges
triggers: spatial, origin, transform-origin, popover, menu, sheet, symmetry, enter, exit, rubber band, boundary, overscroll, direction
pulls: apple.materials
weight: 7
---

# Spatial consistency

- **Enter and exit along the same path.** A panel that slides in from the right dismisses to the right. In-from-right / out-the-bottom feels disconnected.
- **Anchor interactions to their source.** Menus, popovers, and sheets originate from the triggering element: set `transform-origin` to the trigger so the spatial relationship is obvious.
- **Mirror the easing on reversible transitions** so the outbound path matches the return (inverse cubic-bézier control points).
- **Hint in the direction of the gesture.** Intermediate frames should telegraph the outcome, not interpolate blindly. Control Center modules grow up and out toward the finger.

# Rubber-banding

At an edge, resist progressively instead of stopping hard. A hard stop reads as frozen; continuous resistance reads as responsive with nothing more here.

```js
// The further past the bound, the less it follows. Real things slow before they stop.
function rubberband(overshoot, dimension, constant = 0.55) {
  return (overshoot * dimension * constant) / (dimension + constant * Math.abs(overshoot));
}
```

Use on sheet overdrag, horizontal carousel ends, and pull-to-refresh. Pair with a spring return that carries the release velocity; a hard `scroll-behavior: smooth` return is the tell of an assembled page.
