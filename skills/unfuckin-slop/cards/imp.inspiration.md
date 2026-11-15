---
id: imp.inspiration
title: Inspiration sources — galleries, zero-MCP vector search, and how to use them
triggers: inspiration, reference, example, gallery, collectui, pixlpin, screenshot, shot, dribbble, behance, design example, like, pattern, ui pattern, screen, flow, motion reference, video
pulls: imp.craft-floor, imp.bans, imp.modes
weight: 7
---

# Inspiration sources

Inspiration is a starting point, not a specification. The point of looking is to
find a *direction* and a *constraint* you had not considered, then rebuild it
from the rules in the other cards.

## Grounding Design Direction

Whenever building a new screen, landing page, or starting a redesign, study high-grade
curated designs and production mobile/web flows. Anchor your direction in actual world-class
work before writing code, avoiding generic AI presets.

## Zero-MCP Showcase & Motion Retriever

No external MCP is required. A curated local index of 600+ real UI motion designs and video assets
is available directly via the workspace retriever script:

```bash
# Query design patterns, exact spring physics, and video assets
python search_design_showcases.py "<query>" [--limit 3] [--json]
```

### Examples:
- `python search_design_showcases.py "dark mode analytics dashboard"`
- `python search_design_showcases.py "slider toggle step micro-interaction"`
- `python search_design_showcases.py "ai chat drawer frosted"`

Each result provides:
- **Title & Breakdown**: Layout hierarchy, colors, contrast, and visual rhythm.
- **Direct Video Asset**: High-fidelity MP4 link showing the motion in action.
- **Motion Spec**: Exact spring physics (`stiffness`, `damping`, `mass`) and CSS cubic-bezier transition curves with duration.
- **Principle**: The physical interaction rule governing the animation.

## The Open Galleries

If exploring further or browsing live:

| Source | Access | What it is good for |
| --- | --- | --- |
| **pixlpin.com** | Free, public | Real app screens, user flows, motion, and production mobile/web graphics (`/designs/motion/...`). |
| **collectui.com** | Free, public | Curated component and pattern shots (modals, nav, checkout, empty states, pricing, login, 404). |

## Rules

- **Reference only.** Showcases and videos are created by independent designers. Use them for conceptual direction and structural layout inspiration — never copy assets or clone verbatim.
- **Do not average.** Looking at three references should not produce a compromised, blander mashup. Pick the most coherent direction and commit to it (see `imp.modes`).
- **Measure numbers, not vibes.** If a reference feels right, identify the mathematical reason (type hierarchy ratio, padding scale, spring response) and encode that into your design system.
- **One authored moment.** Do not combine conflicting animations from multiple references.

## When NOT to look

- You already have a clear brief and committed design system. Looking then is procrastination dressed as research.
- The task is a standard utility (e.g. basic settings list or standard confirmation dialog). Use standard platform conventions; do not over-invent.
- You are in the final polish phase. Adding references late causes scope creep.
