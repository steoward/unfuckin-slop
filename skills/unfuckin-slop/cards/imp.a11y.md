---
id: imp.a11y
title: Accessibility — the parts that are not optional
triggers: accessibility, a11y, contrast, focus, keyboard, aria, screen reader, alt text, target size, zoom, semantics
pulls: apple.motion-a11y, imp.states
weight: 9
---

# Accessibility

- **Contrast:** body and placeholder text ≥4.5:1, large text (≥24px or ≥19px bold) ≥3:1, UI boundaries and focus indicators ≥3:1.
- **Focus is designed, not removed.** `:focus-visible` with a ≥2px ring and visible offset, themed from the palette. Never `outline: none` without a replacement.
- **Keyboard reaches everything.** Logical tab order, no traps, Escape closes overlays, focus returns to the trigger, focus moves into a dialog on open. Skip link for repeated navigation.
- **Semantic HTML first.** `button`, `a href`, `label`, `nav`, `main`, `dialog`. ARIA only patches what HTML cannot express, and a wrong role is worse than none.
- **Every icon-only control has an accessible name.** `aria-label` or visually hidden text, not a `title` attribute.
- **Images:** decorative `alt=""`; informative alt states the content, not "image of". Charts need a text summary.
- **Target size:** ≥24×24 CSS px minimum, 44×44 preferred for touch. Spacing counts toward the target.
- **Never colour alone** to carry meaning: pair with text, icon, or shape.
- **Motion and transparency** respond to the user's preference (see `apple.motion-a11y`).
- **Text scales to 200%** without loss of content or function; use `rem` and let containers grow.
- **Forms:** visible labels, errors tied with `aria-describedby`, `aria-invalid`, and no error conveyed only by a red border.
