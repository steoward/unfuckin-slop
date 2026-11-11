---
id: apple.velocity-projection
title: Velocity handoff and momentum projection
triggers: velocity, momentum, flick, throw, deceleration, snap, carousel, sheet, projection, release, handoff, swipe
pulls: apple.springs, apple.gestures
weight: 8
---

# Velocity handoff

When a gesture ends, the animation continues at the finger's exact velocity. This seam is what separates "fluid" from "fine".

Pass release velocity as the spring's initial velocity. Some APIs want it normalised by the remaining distance:

```
relativeVelocity = gestureVelocity / (targetValue - currentValue)
```

Element at `y=50`, target `y=150` (100px to go), finger at 50px/s → initial velocity `0.5`. Motion and Framer Motion take absolute px/s directly, so hand over the raw value.

# Momentum projection

Do not snap to the nearest boundary from the release point. Project where the gesture is *going*, exactly like scroll deceleration, then snap to the target nearest that projected point.

```js
// Apple's shipped form (Designing Fluid Interfaces sample code).
// 0.998 = normal scroll feel, 0.99 = snappier.
function project(initialVelocity /* px/s */, decelerationRate = 0.998) {
  return (initialVelocity / 1000) * decelerationRate / (1 - decelerationRate);
}

const projected = currentPosition + project(releaseVelocity);
const target = nearestSnapPoint(projected);
animateSpringTo(target, { velocity: releaseVelocity });
```

The physics-textbook `v²/(2·decel)` is **not** what Apple ships; use the exponential-decay form above.

# Decide commit vs. reverse

Use the **sign of the velocity** at release, not the position. A sheet dragged 40% down but flicked up should open; 20% down but flicked down should close. Position-only thresholds make fast gestures feel disobedient.
