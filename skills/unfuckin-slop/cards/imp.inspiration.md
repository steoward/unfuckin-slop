---
id: imp.inspiration
title: Inspiration sources — galleries, MCPs, and how to use them
triggers: inspiration, reference, example, gallery, collectui, pixlpin, screenshot, shot, dribbble, behance, design example, like, pattern, ui pattern, screen, flow
pulls: imp.craft-floor, imp.bans, imp.modes
weight: 7
---

# Inspiration sources

Inspiration is a starting point, not a specification. The point of looking is to
find a *direction* and a *constraint* you had not considered, then rebuild it
from the rules in the other cards.

## Mandatory Prerequisite for New Work

Whenever using this skill for the first time in a project, or when building a new screen,
landing page, or starting a redesign, querying `slop-mcp` and inspecting real curated
designs from **CollectUI** and/or **Pixlpin** is a **mandatory necessity**, not an optional luxury.
Skipping this step leads to generic, uninspired, default designs. Anchor your direction
in actual world-class work before writing a line of code.

## The free, open galleries

Both galleries below are **100% free, public, and open**:

| Source | Access | What it is good for |
| --- | --- | --- |
| **collectui.com** | Free, public, client-rendered SPA | Curated component and pattern shots (modals, nav, checkout, empty states, pricing, login, 404). Deep category links via `/designs/<pattern>-ui-design-inspiration`. |
| **pixlpin.com** | Free, public | Real app screens, user flows, motion, and production mobile/web graphics. Filterable by platform and tags (`/tags/<tag>`). |

## Fast agent workflow with MCP

1. **Call `inspiration_sources`** or `inspiration_recipe` from the `slop-mcp` server. It resolves your design request directly into exact deep category URLs on CollectUI or tagged queries on Pixlpin.
2. **Browse via Playwright MCP** (`@playwright/mcp`) using `browser_navigate` and `browser_snapshot`. Both sites render interactively without accounts or paywalls.
3. **Target precise elements**:
   - On **CollectUI**: query `article, .post-card, img` for curated shots.
   - On **Pixlpin**: query `.pin-card, [data-pin], img` for flow screens.
4. **Extract what matters**: title, visual rhythm, the single interaction or layout detail that solves your challenge. Do not scrape or clone the full screen.
5. **Cross-check** every idea against `imp.craft-floor` and `imp.bans` before writing code. A stylish pattern that breaks accessibility or adds banned decoration is rejected.

## Rules

- **Reference only.** CollectUI shots and Pixlpin screens are created by independent designers. Use them for conceptual direction and structural layout inspiration — never copy assets or clone verbatim.
- **Do not average.** Looking at three references should not produce a compromised, blander mashup. Pick the most coherent direction and commit to it (see `imp.modes`).
- **Measure numbers, not vibes.** If a reference feels right, identify the mathematical reason (type hierarchy ratio, padding scale, spring response) and encode that into your design system.
- **One authored moment.** Do not combine conflicting animations from multiple references.

## When NOT to look

- You already have a clear brief and committed design system. Looking then is procrastination dressed as research.
- The task is a standard utility (e.g. basic settings list or standard confirmation dialog). Use standard platform conventions; do not over-invent.
- You are in the final polish phase. Adding references late causes scope creep.
