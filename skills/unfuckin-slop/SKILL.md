---
name: unfuckin-slop
description: "Autonomous 3D & Kinetic UI Design Engine for Coding Agents: Model-grounded inspiration via EmbeddingGemma 2 motion vectors, Apple-grade physical craft, and deterministic anti-slop floor."
version: 1.1.0
license: MIT
---

# Unfuckin-Slop

Autonomous 3D & Kinetic UI Design Engine for Coding Agents: Model-grounded inspiration via EmbeddingGemma 2 motion vectors, Apple-grade physical craft, and deterministic anti-slop floor.

This file is the thin layer that is always loaded. The cards are not.

## Workflow Philosophy: Model Leads, Quality Floor Follows

**The Embedded Model (EmbeddingGemma 2 UI motion retriever) LEADS the creative vision as the Creative Director. The skill cards and linting FOLLOW as the Engineering Quality Floor.**

- **Model as Creative Director:** When told to "build a site/screen of your choice" or given any creative brief, coding agents must **FIRST** run `python search_design_showcases.py` (with `--3d` or creative keywords like `"3d spatial hero"`, `"kinetic typography"`, `"interactive canvas"`, `"particle orbit"`) to ground the design in high-impact 3D, WebGL canvas, spatial depth, particle fields, or kinetic typography from the 622 video showcases. Never default to generic, flat templates.
- **Skill as Engineering Floor:** The skill rules (Apple craft, contrast ≥ 4.5:1, keyboard focus, custom scrollbar) then verify, constrain, and polish the implementation **without killing creativity**. High-ambition 3D and kinetic designs must run at 60fps, remain keyboard accessible, and react with authentic physical spring physics.

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

1. **Creative Grounding (Model as Director):** For open-ended briefs or landing pages, FIRST run `python search_design_showcases.py` (with `--3d` or creative keywords) to ground the design in 3D canvas, spatial depth, particle fields, or kinetic typography before writing code.
2. **Name the surface and mode:** `Persuade` and `Experience` demand maximum ambition (3D canvas, liquid glass, kinetic type, spatial tilt). `Operate` and `Read` demand precision, density, and restraint.
3. **Pull the pack** once: `unfslop context "<what you are about to do>"`. Read the cards to calibrate craft rules.
4. **Build the experience:** Implement the 3D/kinetic visual anchor; layer Apple physical craft (pointer-down response, spring physics, interruptibility).
5. **Verify mechanically:** Run `unfslop lint <changed paths>` to catch hard defects without suppressing creative ambition.
6. **Stop:** When the floor is green and the committed 3D/kinetic idea is visible, you are done. Do not gold-plate.

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

- Ground open-ended designs in high-impact 3D, spatial depth, or kinetic motion via the retriever before writing code.
- 3D Canvas, WebGL, particle fields, ambient lighting, and liquid glass are celebrated in `Experience` and `Persuade` modes — never treated as slop when authored as the central interactive experience.
- Feedback starts on **pointer-down**, and continues during the interaction, not only at the end.
- If it can be grabbed, flicked, or dismissed, it is **interruptible**: springs, not CSS transitions or keyframes. Start from the current on-screen value; carry velocity through a reversal.
- Never lock out input during a transition.
- Body text ≥4.5:1, large text ≥3:1. A visible `:focus-visible` ring. Every `:hover` has a focus twin. Custom scrollbars match background and thumb contrast.
- Every interactive element has default, hover, active, focus, disabled, loading, error. Every collection has empty, one, many, loading, error.
- No kicker/eyebrow above a heading. No gradient text. No coloured side stripe above 1px. No nested cards. No `transition: all`.
- One authored motion moment, not the same entrance on every section.
- Reduced motion gets a cross-fade, not a slower slide.
- Controls name their action; errors name the problem and the recovery; no em dashes in copy.
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

## Model-Grounded Inspiration Architecture

Self-contained with **zero external MCP dependencies**:

1. **EmbeddingGemma 2 UI Motion Retriever (Creative Director):** 622 UI motion designs fine-tuned with EmbeddingGemma 2 (~740M multimodal params).
   - Run: `python search_design_showcases.py "<query>" [--3d] [--limit 3] [--json]`
   - Broad or empty queries return 5 distinct creative archetypes (3D Spatial Hero, Kinetic Type & Liquid Glass, 3D Bento Tilt, Cybernetic Interface, Camera Orbit).
   - Returns: Three.js/Canvas scaffolds, spatial depth (`perspective: 1200px`), spring physics (`stiffness`, `damping`), CSS curves, and direct MP4 URLs.
2. **Skill (this file + 30 cards):** Thin layer and on-demand atom cards.
3. **Context Router (`unfslop`):** Serves relevant cards without context bloat (`unfslop context "<task>"`).
4. **Mechanical Floor (`unfslop lint`):** 18 deterministic checks catching eyebrow headings, fake icons, `transition: all`, and generic slop.

## Attribution

Distilled from Emil Kowalski's Apple Design skill (after Apple's WWDC talks) and Paul Bakaus' Impeccable (Apache-2.0). Independent rewrite, not an endorsed copy. See `NOTICE.md` for the full statement.
