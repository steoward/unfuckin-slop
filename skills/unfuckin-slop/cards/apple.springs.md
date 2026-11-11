---
id: apple.springs
title: Springs — damping and response, with Apple's shipped values
triggers: spring, damping, response, bounce, overshoot, settle, motion, animation duration, framer motion, physics, elastic
pulls: apple.interruptibility, apple.velocity-projection
weight: 9
---

# Springs

A pre-scripted fixed-duration animation cannot respond to new input. A spring can: new input only changes the target, and the motion stays continuous.

Apple replaced the physics triplet (mass, stiffness, damping) with two designer-facing parameters:

- **Damping ratio** — overshoot. `1.0` is critically damped: no bounce, smooth settle. Below `1.0` overshoots and oscillates; lower is bouncier.
- **Response** — how quickly the value reaches the target, in seconds. Lower is snappier. **This is not duration**: a spring has no fixed duration, its settle time emerges from the parameters.

## Defaults

- Start most UI at **damping 1.0**, response 0.3–0.4. Graceful, non-distracting.
- Add bounce (**damping ~0.8**) **only when the gesture carried momentum** (flick, throw, drag release). Overshoot on a menu that merely faded in feels wrong; overshoot on a card you flicked feels right.

## Values Apple ships

| Interaction | Damping | Response |
| --- | --- | --- |
| Move / reposition (e.g. PiP) | 1.0 | 0.4 |
| Rotation | 0.8 | 0.4 |
| Drawer / sheet | 0.8 | 0.3 |

```js
import { animate } from 'motion';

// Default: critically damped, no overshoot
animate(el, { y: 0 }, { type: 'spring', bounce: 0, duration: 0.4 });

// Momentum release: a little bounce, only because a flick preceded it
animate(el, { y: target }, { type: 'spring', bounce: 0.2, duration: 0.4 });
```

In Motion / Framer Motion, `bounce` + `duration` maps closely to Apple's damping + response. House style: damping 1.0 everywhere, bounce reserved for physical, momentum-driven interactions.

# Smell test

If a designer asks "how long is this animation" and the honest answer is a fixed number for a gestural surface, the tool is wrong. If every element on the page bounces, none of them means anything.
