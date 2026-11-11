---
id: imp.craft-floor
title: The craft floor — the checks that ship or block
always: true
triggers: craft floor, quality, verify, contrast, spacing, states, browser surfaces, checklist, ship, review
pulls: imp.bans, imp.a11y
weight: 10
---

# Craft floor

Load this before any UI edit. These are checks on the built result, not intentions. Run them together in one batched look at the render.

- **Contrast.** Body and placeholder text ≥4.5:1, large text ≥3:1. On coloured surfaces tint secondary text from that hue, or use the foreground; never neutral gray.
- **Depth.** Shadows carry an offset and a soft blur. A zero-offset coloured halo is decoration, not depth.
- **Spacing.** Tight groups, generous separation, more space above a heading than below it. Read the computed values, not the source intention.
- **Type.** Body measure 65–75ch, display max ~6rem, tracking floor -0.04em, balanced headings, obvious scale and weight steps. Run the real copy at every breakpoint and fix what overflows.
- **Motion.** One authored moment, not scattered effects and not one identical entrance on every section. Exponential ease-out from an already-visible default. Reach past transform and opacity: blur, backdrop-filter, clip-path, mask, and shadow belong to the palette when they stay smooth.
- **States.** Hover, active, focus-visible, disabled, loading, error, empty. Plus real content, working controls, responsive composition.
- **Browser surfaces.** The parts you did not draw still carry the design: text selection, caret, custom scrollbars, focus rings, underline offset, tabular numerals. Theme them from the palette. This is the cheapest signal that a page was built rather than assembled, and the one models skip most reliably.
- **Copy.** The product's own language. Controls name their action; errors name the problem and the recovery.
- **Coverage.** Every brief requirement present and findable within seconds.

# Rule

The floor holds the mechanics; it never picks the direction. With every check green, spend the page on the committed world.
