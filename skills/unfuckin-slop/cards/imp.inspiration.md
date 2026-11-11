---
id: imp.inspiration
title: Inspiration sources — galleries, MCPs, and how to use them
triggers: inspiration, reference, example, gallery, collectui, pixlpin, mobbin, refero, screenshot, shot, dribbble, behance, design example, like, pattern, ui pattern
pulls: imp.craft-floor, imp.bans, imp.modes
weight: 7
---

# Inspiration sources

Inspiration is a starting point, not a specification. The point of looking is to
find a *direction* and a *constraint* you had not considered, then rebuild it
from the rules in the other cards.

## The galleries

| Source | Access | What it is good for |
| --- | --- | --- |
| **collectui.com** | Free, public, client-rendered SPA | Component and screen shots (modals, nav, checkout, empty states, pricing). Curated from Dribbble. |
| **pixlpin.com** | Free, public | Real app screens, user flows, motion, graphics. Searchable. |
| **Mobbin** | Paid (Pro/Team/Enterprise); official MCP at `https://api.mobbin.com/mcp` (OAuth) | 621k+ real screens and flows from shipped products. The strongest single source for product UI. |
| **Refero** | Paid; official MCP at `https://api.refero.design/mcp` (OAuth/Bearer) | Real screens + styles, with `DESIGN.md` extraction (colours, type, spacing). |
| **Refero Styles** (`styles.refero.design`) | Public style pages | AI-readable `DESIGN.md` for 2000+ sites. |

## How to browse them (agent workflow)

1. Get entry URLs from the `inspiration_sources` MCP tool, or construct them directly.
2. **Use the Playwright MCP server** (`@playwright/mcp`) to `browser_navigate`, then `browser_snapshot` / `browser_take_screenshot`. These galleries are JavaScript apps; plain HTTP fetch returns an empty shell.
3. For login-gated galleries (Mobbin, Refero), sign in once via Playwright MCP and save storage state (`storageState`); reuse it across sessions.
4. Extract: title, designer/product, image URL, the one thing that makes it work. Do not extract the whole page.
5. **Cross-check** every borrowed idea against `imp.craft-floor` and `imp.bans` before it enters the build. A beautiful side-stripe is still banned.

## Rules

- **Copyright.** CollectUI shots are Dribbble work; Mobbin/Refero are licensed. Use for inspiration and reference only — never redistribute, never paste verbatim, never ship a clone.
- **Do not average.** Three references should not produce a fourth, blander thing. Pick the strongest and commit to it (see `imp.modes`).
- **Numbers, not vibes.** If a reference works, find the measurable reason (contrast, spacing, timing) and reproduce that, not the pixels.
- **One authored moment.** Borrowing motion from five references gives you five motions; keep one.

## When NOT to look

- You already have a clear brief and a committed direction. Looking then is procrastination dressed as research.
- The task is a settings screen, a form, or an error state. Use known patterns; do not invent.
- You are about to ship. References at the end become scope creep.
---

## Attribution

The galleries are independent products; neither endorses this skill. See their own terms before any automated access.
