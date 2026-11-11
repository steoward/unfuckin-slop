---
id: apple.interruptibility
title: Interruptibility — the single most important principle
triggers: interrupt, reverse, redirect, mid-flight, cancel, animation, presentation value, keyframes, transitions, velocity, gesturable
pulls: apple.springs, apple.velocity-projection
weight: 10
---

# Interruptibility

The thought and the gesture happen in parallel. Every animation the user can touch must be interruptible and redirectable at any instant: grab a closing modal and it follows the finger, rather than finishing the close and then reopening.

Rules:

1. **Never lock out input during a transition.** No `pointer-events: none` while a sheet settles, no queued taps.
2. **Animate from the presentation (current on-screen) value, never the target.** On interrupt, read the live transform and start from it. Starting from the logical target produces a visible jump.
3. **Avoid CSS transitions and `@keyframes` for gesture-driven motion.** They cannot be grabbed and reversed smoothly; a new transition restarts from a keyframe. Springs animate from the current value by default.
4. **Blend velocity on reversal.** Swapping one animation for another at a reversal creates a velocity discontinuity, a brick wall. Use a spring that re-targets while carrying the current velocity.
5. **Decompose 2D motion into independent X and Y springs.** One spring on a 2D distance desyncs when the axes have different velocities.

```js
// On interrupt, start where the element actually is
const live = getComputedStyle(el).transform; // matrix(...)
const y = new DOMMatrixReadOnly(live).m42;
animate(el, { y: target }, { type: 'spring', bounce: 0, duration: 0.4, velocity: currentVelocity });
```

# Decision rule

If an element can be grabbed, flicked, dismissed, or re-opened, it is gesture-driven, and a duration-based ease is the wrong tool regardless of how good the curve looks in isolation.
