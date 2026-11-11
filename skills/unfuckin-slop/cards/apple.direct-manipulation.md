---
id: apple.direct-manipulation
title: Direct manipulation — 1:1 tracking, grab offset, pointer capture
triggers: drag, swipe, grab, pointer events, setPointerCapture, tracking, offset, carousel, slider, drawer, pan, touch
pulls: apple.interruptibility, apple.springs
weight: 8
---

# Direct manipulation

Touch and content move together. When the user drags something it stays glued to the finger, at the offset where they grabbed it.

- **Respect the grab offset.** Snapping the element to the pointer's centre on grab breaks the illusion instantly.
- **Use Pointer Events with `setPointerCapture`** so tracking continues when the pointer leaves the element's bounds.
- **Keep a short velocity history** (last few `pointermove` events with timestamps), not just the current point. You need velocity at release, and you cannot reconstruct it after the fact.

```js
el.addEventListener('pointerdown', (e) => {
  el.setPointerCapture(e.pointerId);
  const grabOffset = e.clientY - el.getBoundingClientRect().top;
  let history = [{ t: e.timeStamp, y: e.clientY }];

  const move = (ev) => {
    const y = ev.clientY - grabOffset;
    el.style.transform = `translateY(${y}px)`;
    history.push({ t: ev.timeStamp, y: ev.clientY });
    if (history.length > 5) history.shift();
  };

  const up = () => {
    el.removeEventListener('pointermove', move);
    el.removeEventListener('pointerup', up);
    release(velocityOf(history)); // see apple.velocity-projection
  };

  el.addEventListener('pointermove', move);
  el.addEventListener('pointerup', up);
});
```

# Failure modes

- Tracking only after a threshold *and* jumping the element to the pointer: two discontinuities at once.
- Using `mousedown`/`mousemove`: no touch, no pen, no capture.
- Recomputing layout per move (`getBoundingClientRect` inside the handler): jank at exactly the wrong moment. Cache it on pointer-down.
