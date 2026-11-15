---
name: unfuckin-slop
description: Design and review frontend interfaces with Apple-grade motion craft and Impeccable's direction discipline. Use when building, redesigning, critiquing, or polishing any UI (websites, landing pages, dashboards, app screens, components, design systems), or when working on gesture and spring interactions, typography, colour, layout, motion, accessibility, states, and anti-slop review. Retrieves only the rules the current task needs.
version: 1.1.0
license: MIT
---

# Unfuckin-Slop

Two design bodies of knowledge, cut into atom cards and served on demand: **Apple Design** (fluid interfaces, physical motion, WWDC craft) and **Impeccable** (direction, craft floor, anti-slop discipline). This file is the thin layer that is always loaded. The cards are not.

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

1. **Name the surface and the mode.** A tool's landing page is Persuade; its settings screen is Operate. Mode decides how much ambition is appropriate.
2. **Establish the design direction.** When designing or animating a component, query the curated UI motion retriever: `python search_design_showcases.py "<query>" --json`. It supplies visual hierarchy, real MP4 video references, and exact spring physics (`stiffness`, `damping`, `mass`) without requiring external MCP servers.
3. **Pull the pack** for the task, once. Read it, then act. Do not re-run it for every edit.
4. **Build or review** using the cards. When a rule conflicts with a pinned brief, the brief wins unless the card says "ban".
5. **Verify mechanically** before claiming done: `unfslop lint <changed paths>`. Then look at the rendered result at the size it ships at, and batch your fixes into one pass.
6. **Stop.** When the floor is green and the committed idea is visible, you are done. Do not gold-plate.

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

- Ground the direction in real, physical craft and intentional layout before laying down code.
- Feedback starts on **pointer-down**, and continues during the interaction, not only at the end.
- If it can be grabbed, flicked, or dismissed, it is **interruptible**: springs, not CSS transitions or keyframes. Start from the current on-screen value; carry velocity through a reversal.
- Never lock out input during a transition.
- Body text ≥4.5:1, large text ≥3:1. A visible `:focus-visible` ring. Every `:hover` has a focus twin.
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

This skill operates completely self-contained with **zero external MCP dependencies**:

1. **Skill (this file + 30 cards).** Core design principles, physical motion rules, quality floor, and router. The thin layer you are reading.
2. **Context Router (`unfslop`).** Rust CLI that serves relevant cards on-demand without context bloat (`unfslop context "<task>"`).
3. **EmbeddingGemma 2 UI Motion Retriever.** A curated vector index of 600+ real UI motion designs and high-fidelity video streams fine-tuned with EmbeddingGemma 2.
   - Run: `python search_design_showcases.py "<query>" [--limit 3] [--json]`
   - Returns: Exact visual layout hierarchy, spring physics parameters (`stiffness`, `damping`, `mass`), CSS cubic-bezier curves with timing, and direct MP4 video references.
   - Bridges the gap for LLMs and coding agents that do not ingest video directly, giving them mathematically grounded parameters and visual layout references before writing code.
4. **Mechanical Floor (`unfslop lint`).** 18 deterministic checks catching eyebrow headings, fake icon costumes, `transition: all`, and generic slop.

## Attribution

Distilled from Emil Kowalski's Apple Design skill (after Apple's WWDC talks) and Paul Bakaus' Impeccable (Apache-2.0). Independent rewrite, not an endorsed copy. See `NOTICE.md` for the full statement.
