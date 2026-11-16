# Unfuckin-Slop

Autonomous UI & Kinetic Design System for Coding Agents: Production-grade component library, model-grounded inspiration, and anti-slop quality floor.

Two of the best frontend design skills, **Apple Design** (Emil Kowalski, distilled from Apple's
WWDC interface talks) and **Impeccable** (Paul Bakaus, Apache-2.0), fused into **30 atom cards** and
served on demand by a **zero-dependency Rust binary** — paired with a curated 950 UI design system showcase library
(622 Pixlpin visual showcases + 328 MotionSites full prompt blueprints) fine-tuned with Google DeepMind's **EmbeddingGemma 2**.

The problem it solves is not knowledge. It is context. Loading both skills means ~10,000 tokens
before you write a line of CSS, and most of it is irrelevant to the one thing you are doing. Here the
always-on layer is ~1,600 tokens, and the router pulls one to four cards (usually ~1,700) that match
the task in front of you.

```
SKILL.md              always loaded, ~1.6k tok     the protocol + the non-negotiables + the index
     │
     ├─ unfslop context "draggable sheet that snaps" ranks 29 cards, prints 4 that fit 2k tok
     │      └─ cards/apple.springs.md               one idea, one page, only when asked for
     │
     └─ unfslop lint src/                           the mechanical half of the quality floor
```

## Quick start

```bash
cargo build --release          # builds unfslop
target/release/unfslop doctor
target/release/unfslop context "settings page with destructive actions"
```

Put `unfslop` (or `unfslop.exe`) somewhere on `PATH`, or use the copy installed with the skill.

### Install as an agent skill

```bash
unfslop install                  # → .claude/skills/unfuckin-slop
unfslop install --user           # → ~/.claude/skills/unfuckin-slop
unfslop install --dir path/to/skills/unfuckin-slop
```

That writes `SKILL.md`, all 29 cards, `NOTICE.md`, and a copy of the binary at `bin/unfslop`, so the
skill keeps working on a machine with no Cargo toolchain. Any SKILL.md-compatible agent can use it
(Claude Code, Codex, Cursor, Copilot, and friends); point it at the folder.

For this repository itself, the skill is already in `skills/unfuckin-slop/`. Agents that scan
`.claude/skills` need the install step.

## Commands

| Command | What it does |
| --- | --- |
| `unfslop context "<task>"` | The main command. Ranks cards, prints only those that fit the budget. |
| `--budget N` | Token ceiling for the pack. Default 2000. |
| `--limit N` | Card ceiling. Default 6. |
| `--mode M` | Force a mode: `build`, `motion`, `gesture`, `critique`, `polish`, `system`, `a11y`, `native`. |
| `--brief` | Headers and token costs only, no bodies. |
| `--all` | Ignore budget and limit (rarely what you want). |
| `unfslop get <id>` | One card, full text. |
| `unfslop search "<query>"` | BM25 over titles, triggers, ids and bodies. Scores shown. |
| `unfslop cards` | The index: id, token cost, title. No bodies. |
| `unfslop lint [paths]` | 18 deterministic anti-slop and craft checks. |
| `unfslop install` | Write the skill and binary to a skills directory. |
| `unfslop doctor` | Library size, thin-layer share, install state. |
| `unfslop stats` | Tokens by source, largest cards. |
| `--json` | Any read command emits structured output. |

## The cards

**Apple craft** — `response`, `direct-manipulation`, `interruptibility`, `springs`,
`velocity-projection`, `spatial`, `gestures`, `materials`, `typography`, `motion-a11y`,
`multimodal`, `principles`, `process`.

Numbers are preserved, not paraphrased away: damping 1.0 / response 0.4 for a move, 0.8 / 0.3 for a
sheet, the `0.998` momentum projection, the grab offset, the -0.04em tracking floor, the ~300ms tap
delay to delete.

**Direction and QA** — `workflow`, `modes`, `craft-floor`, `bans`, `slop-test`, `layout`, `typeset`,
`color`, `motion`, `states`, `copy`, `a11y`, `performance`, `critique`, `polish`, `system`.

The permanent ban (an eyebrow above a heading), the refused defaults (side stripes, gradient text,
hard shadows, nested cards, emoji as icons), the four modes, and the review format that refuses to
average the weakest axis away.

Each card carries front matter the router uses:

```
id: apple.interruptibility
title: Interruptibility — the single most important principle
triggers: interrupt, reverse, redirect, mid-flight, cancel, animation, ...
pulls: apple.springs, apple.velocity-projection
weight: 10
```

`always: true` marks the craft floor, which is placed second in every pack so it is read rather than
skipped.

## Lint

`unfslop lint src/` reports `path:line severity rule`, the problem, and the fix. Exit code 1 on error.

| Group | Checks |
| --- | --- |
| `ban.*` | eyebrow/kicker, gradient text, side stripe >1px, hard offset shadow, zero-offset halo, `transition: all` |
| `type.*` | tracking below -0.04em, px root font size |
| `a11y.*` | missing alt, clickable div, removed outline, hover without focus-visible |
| `motion.*` | transform motion without reduced-motion, CSS-driven gesture motion |
| `perf.*` | animating layout properties |
| `copy.*` | em dash, "click here", lorem ipsum |

`--ignore ban` drops a whole group; `--ignore a11y.img-alt` drops one rule; `--fail-on warn` is
stricter, `--fail-on never` is for exploratory runs. Fix the cause, do not mute the rule.

A `.slopignore` in the working directory excludes unrelated paths (one prefix per line, `#` for
comments), so tool state and archives do not drown the findings.

`fixtures/` is a deliberate violation set: `unfslop lint fixtures` finds 19 findings (6 errors).

## Design notes

- **Zero dependencies, no async runtime.** The whole tool is ~2,000 lines of std Rust. Builds offline,
  starts in milliseconds, and has no supply chain to audit.
- **Embedded cards with a disk override.** `build.rs` bakes the cards into the binary so it works
  anywhere; if `UNFUCKIN_SLOP_HOME` or a `cards/` directory sits next to the binary or the cwd, that
  wins, so editing a card is a rebuild-free operation.
- **Budget is estimated, not tokenized.** Four characters per token keeps the tool instant and errs on
  the safe side. The pack never pads to fill the budget: if a mandated card does not fit, it stops.
- **Relevance is thresholded.** Extras must score at least 25% of the best match, so a big budget
  cannot smuggle in weak material.
- **The linter is the point of the second half.** A model will claim it checked contrast, states, and
  focus rings. It will not. These 18 checks are deterministic, cheap, and cite the rule they come
  from.

## Verify

```bash
cargo test                     # unit & integration tests
cargo build --release          # builds standalone unfslop
target/release/unfslop context "spring sheet snap" --budget 1200
target/release/unfslop lint fixtures; echo "exit=$?"
```

## Autonomous UI & Kinetic Design System

Unfuckin-Slop operates completely self-contained with **zero external MCP dependencies**.

### Workflow Philosophy: Component Library & Design Architecture First
1. **Designs & Components First:**
   When told to build any site, screen, dashboard, or landing page, coding agents **FIRST** query `python search_design_showcases.py` (with `--components`, `--category <name>`, or search terms) to pull real UI architecture: Hero layouts, Navbars, Bento cards, Button styles, Lighting & Atmosphere tokens, and Color systems from the 950 curated showcase library (622 Pixlpin visual showcases + 328 MotionSites full prompt blueprints).
2. **Visual Hierarchy & Styling:**
   Assemble the page with distinct typographic scale, dark/light surface tokens, and ambient lighting.
3. **Organic Physics:**
   Transitions and springs are natural, quiet implementation details (duration, cubic-bezier curves, or spring stiffness/damping). Websites and web apps do NOT use audio, sound effects, or vibration gimmicks.
4. **Mechanical Anti-Slop Quality Floor:**
   Run `unfslop lint` to verify the implementation against 18 deterministic checks: contrast ≥ 4.5:1, keyboard focus rings, no kicker eyebrows, no gradient text, no side stripes, and no `transition: all`.

### How agents use it:
```bash
# Pull ready-to-use production UI component tokens (Buttons, Bento Cards, Navbars, Atmosphere)
python search_design_showcases.py --components

# Open-ended or empty queries return 6 industry-standard website archetypes with concrete component blueprints
python search_design_showcases.py ""

# Query specific UI patterns, SaaS dashboards, or fintech interfaces
python search_design_showcases.py "SaaS analytics dashboard" --limit 3

# Filter by category (e.g. Hero, Bento, SaaS, Ecommerce, Portfolio)
python search_design_showcases.py --category SaaS

# Extract full prompt blueprints with verbatim code, fonts, and Tailwind classes
python search_design_showcases.py "liquid glass" --full
```

### What it provides:
- **Production UI Component Tokens (`--components`)**: Ready-to-use button primitives (glow CTA, ghost), Bento card surface elevations, floating pill navigation bars, and radial atmosphere lighting tokens.
- **Visual hierarchy & layout breakdown**: Surface contrast, spatial elevation, typography scale, and color systems.
- **Physical Spring & Motion Parameters**: Exact `stiffness`, `damping`, durations, and CSS cubic-bezier curves.
- **Direct Video Reference**: Direct link to the high-frame-rate interaction video.

The agent uses these concrete UI blueprints to build production-grade interfaces, then mechanically verifies them with `unfslop lint`.

## Attribution and licence

MIT for the code. The knowledge is an independent distillation of two Apache-2.0/MIT-licensed skills;
see `NOTICE.md`. Neither author endorses this project. If you want the full source material, install
the originals: `emilkowalski/skills` (`apple-design`) and `pbakaus/impeccable`.
