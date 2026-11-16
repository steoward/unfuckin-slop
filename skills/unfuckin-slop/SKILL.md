---
name: unfuckin-slop
description: "Autonomous UI & Kinetic Design System for Coding Agents: Production-grade component library, model-grounded inspiration, and anti-slop quality floor."
version: 1.1.0
license: MIT
---

# Unfuckin-Slop

Autonomous UI & Kinetic Design System for Coding Agents: Production-grade component library, model-grounded inspiration, and anti-slop quality floor.

This file is the thin layer that is always loaded. The cards are not.

## Workflow Philosophy: Component Library & Design Architecture First

**Production-grade UI component architecture and visual hierarchy lead. Clean kinetic craft and mechanical anti-slop linting follow as the engineering floor.**

- **Real UI Architecture First:** When tasked with building any website, interface, dashboard, or landing page, coding agents must **FIRST** pull concrete UI components and layout blueprints: Hero layouts, Navigation bars, Bento feature grids, Button styles, Lighting & Atmosphere tokens, and Color systems. Query `python search_design_showcases.py` (with `--components`, `--category <name>`, or search terms) to ground the interface in 950 production-grade design showcases (622 curated visual showcases + 328 MotionSites full prompt blueprints). Pass `--full` when you need verbatim code blueprints (font imports, Tailwind classes, exact CSS/shader formulas). Never default to generic, unstyled, or flat templates.
- **Organic Physics (Quiet Implementation Details):** Transitions and springs are natural, quiet implementation details (smooth 60fps Framer Motion or CSS cubic-bezier curves). Websites and web apps do NOT use audio, sound effects, or vibration gimmicks.
- **Skill as Engineering Floor:** The skill rules (contrast ≥ 4.5:1, keyboard focus, custom scrollbars, state matrices) verify and polish the implementation without suppressing design ambition.

## Rule 0 — do not read the cards directly

Run the router. It ranks the cards for the task and prints only what fits the budget:

```bash
unfslop context "<what you are about to do>"     # default: ~2000 tok, max 6 cards
unfslop context "draggable sheet that snaps" --budget 1200 --brief
unfslop get apple.interruptibility               # one card, when you need a specific rule
unfslop search "focus ring"                      # find a card by topic
unfslop cards                                    # the whole index, no bodies
```

If `unfslop` is not on PATH, use `bin/unfslop` (or `bin/unfslop.exe`) inside this skill's folder. If the binary cannot run at all, fall back to reading **exactly one** file, `cards/<id>.md`, named by the index at the bottom of this file. Never read `cards/` in bulk, and never load a card whose rule the task does not touch.

Do not show the pack to the user. It is working context, not output.

## Protocol

1. **Designs & Components First:** Query `python search_design_showcases.py` (or pass `--components`, `--category <name>`) to pull real UI architecture: Hero layouts, Navbars, Bento cards, Button styles, Lighting & Atmosphere tokens, and Color systems. Pass `--full` when you need verbatim prompt blueprints.
2. **Visual Hierarchy & Styling:** Assemble the page with distinct typographic scale, dark/light surface tokens, and ambient lighting. Select surface mode (`Persuade`, `Experience`, `Operate`, or `Read`).
3. **Organic Physics:** Transitions and springs are natural, quiet implementation details (no sound/haptic gimmicks, no `transition: all`). Feedback starts on pointer-down.
4. **Mechanical Verification:** Run `unfslop lint <changed paths>` to ensure zero slop (contrast ≥ 4.5:1, keyboard focus rings, no eyebrows, no gradient text, no side stripes).
5. **Stop:** When the floor is green, components are fully styled, and the design is cohesive, you are done. Do not gold-plate.

## Modes

| Mode | Picked when the task is | `--mode` |
| --- | --- | --- |
| Build | new screen, component, page, or redesign | `build` |
| Motion | springs, drag, swipe, sheets, momentum, interruption | `motion` or `gesture` |
| Review | critique, audit, score, "is this good" | `critique` |
| Polish | final pass, tighten, clean up | `polish` |
| System | tokens, DESIGN.md, theme, palette | `system` |
| A11y | contrast, focus, keyboard, reduced motion | `a11y` |
| Native | iOS, iPadOS, macOS, Android conventions | `native` |
| Inspire | find references, galleries, patterns, examples | `inspire` |

`context` infers the mode from your wording; pass `--mode` when it guesses wrong.

## Never break these

These are true even if you never open a card.

- Ground interfaces in real UI architecture and component blueprints via the retriever before writing code.
- Ambient lighting, glowing accents, Bento grids, and tactile depth are celebrated — never treated as slop when authored with intentional hierarchy.
- Feedback starts on **pointer-down**, and continues during the interaction, not only at the end.
- If it can be grabbed, flicked, or dismissed, it is **interruptible**: springs, not linear CSS keyframes. Start from the current on-screen value; carry velocity through a reversal.
- Never lock out input during a transition.
- Body text ≥4.5:1, large text ≥3:1. A visible `:focus-visible` ring. Every `:hover` has a focus twin. Custom scrollbars match background and thumb contrast.
- Every interactive element has default, hover, active, focus, disabled, loading, error. Every collection has empty, one, many, loading, error.
- No kicker/eyebrow above a heading. No gradient text. No coloured side stripe above 1px. No nested cards. No `transition: all`.
- One authored motion moment, not the same entrance on every section.
- Reduced motion gets a cross-fade, not a slower slide.
- Controls name their action; errors name the problem and the recovery; no em dashes in copy.
- No audio, sound effects, or vibration gimmicks on standard web interfaces.
- Refinement preserves; redesign replaces. Never silently repair drifted product context.
- Verify at shipped sizes. The weakest axis is the verdict; do not average it away.
- When two directions are live, commit. Splitting the difference is how slop is made.

## Card index

**Apple craft**
`apple.response` `apple.direct-manipulation` `apple.interruptibility` `apple.springs` `apple.velocity-projection` `apple.spatial` `apple.gestures` `apple.materials` `apple.typography` `apple.motion-a11y` `apple.multimodal` `apple.principles` `apple.process`

**Direction and QA**
`imp.workflow` `imp.modes` `imp.craft-floor` `imp.bans` `imp.slop-test` `imp.layout` `imp.typeset` `imp.color` `imp.motion` `imp.states` `imp.copy` `imp.a11y` `imp.performance` `imp.critique` `imp.polish` `imp.system` `imp.inspiration`

`imp.craft-floor` is marked always-on and usually appears in the pack without being asked for. That is intentional; it is the checklist that catches what taste misses.

## Lint

`unfslop lint <paths>` scans CSS, HTML, JSX/TSX, Vue, Svelte, and Astro for 18 deterministic tells: eyebrow labels, gradient text, side stripes, hard and zero-offset shadows, `transition: all`, animating layout properties, tracking below -0.04em, px root font sizes, missing alt, clickable divs, removed outlines, hover without focus-visible, transform motion without reduced-motion, CSS-driven gesture motion, em dashes, "click here", and lorem ipsum.

Each finding prints `path:line severity rule`, the problem, and the fix. Exit code is 1 on error by default; use `--fail-on warn` to be stricter. Do not suppress a finding to get a green run. Fix the cause, or say why the rule does not apply.

## Review output

```
Verdict:   ships | ships with fixes | does not ship
Critical:  what / why (card id) / fix
Improve:   what / why / fix
Craft:     the small things
Works:     name it specifically
Scores:    hierarchy, clarity, craft, a11y, coherence (1-5, one line each)
```

No praise padding. Distinguish taste from defect: "I would have picked another typeface" is not a finding; "tracking is -0.06em, letters touch" is.

## UI Design System & Component Library Architecture

Self-contained with **zero external MCP dependencies**:

1. **EmbeddingGemma 2 UI Design System & Component Engine:** 950 curated visual showcases (622 Pixlpin motion showcases + 328 MotionSites full prompt blueprints) fine-tuned with EmbeddingGemma 2 (~740M multimodal params).
   - Component Library: Pass `--components` to get production-ready UI tokens (Button Primitives, Card & Bento Primitives, Navigation Primitives, Lighting & Atmosphere Primitives).
   - Search: `python search_design_showcases.py "<query>" [--components] [--category <name>] [--list-categories] [--3d] [--liquid-glass] [--limit 3] [--full] [--json]`
   - Full Blueprints: Pass `--full` to receive complete, production-grade blueprints (including font links, Tailwind classes, video scrub event listeners, typewriter hooks, and exact CSS/shader formulas).
   - Open-ended or empty queries return 6 industry-standard website archetypes (Modern SaaS, Fintech & Data, High-End Ecommerce, Creative Studio, Developer Tools, AI-Native Platform).
   - Quiet motion specs: Clean durations and cubic-beziers alongside layout tokens and MP4 asset links.
2. **Skill (this file + 30 cards):** Thin layer and on-demand atom cards.
3. **Context Router (`unfslop`):** Serves relevant cards without context bloat (`unfslop context "<task>"`).
4. **Mechanical Floor (`unfslop lint`):** 18 deterministic checks catching eyebrow headings, fake icons, `transition: all`, and generic slop.

## Attribution

Distilled from Emil Kowalski's Apple Design skill (after Apple's WWDC talks) and Paul Bakaus' Impeccable (Apache-2.0). Independent rewrite, not an endorsed copy. See `NOTICE.md` for the full statement.
