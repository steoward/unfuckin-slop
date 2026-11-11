---
id: apple.response
title: Response — kill latency before anything else
triggers: latency, feedback, press, tap, click, pointerdown, debounce, delay, instant, responsiveness, loading
pulls: apple.direct-manipulation
weight: 9
---

# Response

The moment lag appears, the feeling of directness falls off a cliff. Response is the foundation; polish on top of a laggy press is wasted work.

- **Respond on pointer-down, not on release.** Highlight the instant it is pressed. Waiting for `click` or touch-up feels dead.
- **Audit every latency on the input path.** Debounces, artificial timers, transition waits, the ~300ms tap delay, analytics before state updates. Anything not essential is a regression.
- **Feedback is continuous during the interaction, not just at the end.** A drag, slider, or drawer updates 1:1 the whole way through; never animate only when the gesture completes.

```css
/* Feedback lives on the press, and it is instant */
.button:active {
  transform: scale(0.97);
  transition: transform 100ms ease-out;
}
```

# Check it

Throttle the CPU 6x and press the control. If the visual acknowledgement arrives after your finger, the interface feels broken no matter how good it looks.

Latency budget for a direct-manipulation surface: input to first visual change under ~16ms, and never a frame where the element ignores the pointer.
