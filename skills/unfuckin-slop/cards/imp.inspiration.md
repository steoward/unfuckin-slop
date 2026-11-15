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

## Creative Grounding (Model as Creative Director)

The Embedded Model (EmbeddingGemma 2 UI motion retriever) **LEADS** the creative vision as Creative Director.
Whenever told to "build a site/screen of your choice" or given a creative brief, you must **FIRST** run `python search_design_showcases.py` (with `--3d` or creative keywords) to ground the design in high-impact 3D, WebGL canvas, spatial depth, particle fields, or kinetic typography from the 622 video showcases. Avoid falling back to generic AI presets.

## Zero-MCP Showcase & Motion Retriever

No external MCP is required. A curated local index of 622 real UI motion designs and video assets
is available directly via the workspace retriever script:

```bash
# Query design patterns, exact spring physics, and video assets
python search_design_showcases.py "<query>" [--3d] [--limit 3] [--json]

# Empty or broad queries return 5 distinct jaw-dropping creative archetypes
python search_design_showcases.py ""

# Filter exclusively for 3D/WebGL/Kinetic showcases
python search_design_showcases.py --3d
```

### Examples:
- `python search_design_showcases.py --3d` (3D Spatial Heroes, WebGL particles, camera orbits)
- `python search_design_showcases.py "kinetic typography liquid glass refraction"`
- `python search_design_showcases.py "3d bento grid spatial tilt physics"`
- `python search_design_showcases.py "futuristic cybernetic fintech interface"`

Each result provides:
- **Title & Breakdown**: Layout hierarchy, surface elevation, typography, and 3D Canvas setups.
- **Direct Video Asset**: High-fidelity MP4 link showing the motion in action.
- **Motion Spec**: Exact spring physics (`stiffness`, `damping`, `mass`), CSS cubic-bezier transition curves, and CSS 3D rules (`perspective: 1200px`).
- **Principle**: The physical interaction rule governing the animation.

## The Open Galleries

If exploring further or browsing live:

| Source | Access | What it is good for |
| --- | --- | --- |
| **pixlpin.com** | Free, public | Real app screens, user flows, motion, and production mobile/web graphics (`/designs/motion/...`). |
| **collectui.com** | Free, public | Curated component and pattern shots (modals, nav, checkout, empty states, pricing, login, 404). |

## Rules

- **3D Canvas & Kinetic Immersion are NOT slop.** In `Experience` or `Persuade` modes, authoring an interactive 3D canvas with Three.js, particle fields, ambient lighting, or liquid glass elevates the interface above flat template slop. The quality floor ensures it remains accessible and performs at 60fps.
- **Reference only.** Showcases and videos are created by independent designers. Use them for conceptual direction and structural layout inspiration — never copy assets or clone verbatim.
- **Do not average.** Looking at three references should not produce a compromised, blander mashup. Pick the most coherent direction and commit to it (see `imp.modes`).
- **Measure numbers, not vibes.** If a reference feels right, identify the mathematical reason (type hierarchy ratio, padding scale, spring response) and encode that into your design system.
- **One authored moment.** Do not combine conflicting animations from multiple references.

## When NOT to look

- You already have a clear brief and committed design system. Looking then is procrastination dressed as research.
- The task is a standard utility (e.g. basic settings list or standard confirmation dialog). Use standard platform conventions; do not over-invent.
- You are in the final polish phase. Adding references late causes scope creep.
