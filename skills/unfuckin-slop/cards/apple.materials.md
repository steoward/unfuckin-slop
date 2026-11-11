---
id: apple.materials
title: Materials and depth — translucency as hierarchy
triggers: glass, blur, backdrop-filter, translucency, material, vibrancy, depth, shadow, sticky header, toolbar, sheet, scrim, dark mode
pulls: apple.motion-a11y, imp.color
weight: 8
---

# Materials

Translucent material is a floating functional layer: it brings structure without stealing focus. On the web, approximate with `backdrop-filter`.

- **Build nav, toolbars, and sheets as translucent layers** with content scrolling underneath, not opaque bars consuming a fixed strip.
- **Material weight encodes hierarchy.** Heavier/darker materials separate structural regions (sidebars); lighter materials draw attention to interactive elements. **Never stack a light translucent surface on another** — legibility collapses.
- **Bigger surfaces read as thicker:** stronger blur and a deeper shadow than a small chip.
- **Dim to focus, separate to keep flow.** A modal task pairs the surface with a dimming scrim and pushes the background back. A parallel panel uses translucency and offset *without* a scrim. Stacked sheets dim and push back each parent progressively.
- **Vibrancy keeps text legible over changing backgrounds.** Do not use flat gray text on blur: raise contrast, add a little weight and letter-spacing. Put colour on a solid layer, never on the translucent foreground.
- **Scroll edge effects, not hard dividers.** Fade a small blur or gradient where content meets floating chrome, only where the chrome actually overlaps content.
- **Materialise, don't just fade.** Animate blur radius and scale together on enter/exit so the surface reads as a material arriving.

```css
.toolbar {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(20px) saturate(180%);
  border-top: 1px solid rgba(255, 255, 255, 0.4); /* light catching the material */
}
```

# Cost

`backdrop-filter` is expensive on large moving areas. Keep blurred layers static, cap their area, and drop to solid under `prefers-reduced-transparency`.
