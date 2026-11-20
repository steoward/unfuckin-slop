# Unfuckin-Slop

Autonomous UI & Kinetic Design System for Coding Agents: Production-grade component library, model-grounded inspiration, and anti-slop quality floor.

Two of the best frontend design skills, **Apple Design** (Emil Kowalski, distilled from Apple's
WWDC interface talks) and **Impeccable** (Paul Bakaus, Apache-2.0), fused into **30 atom cards** and
served on demand by a **zero-dependency Rust binary** — paired with a curated 950 UI design system showcase library
(622 Pixlpin visual showcases + 328 MotionSites full prompt blueprints) retrieved by a fine-tuned
**all-MiniLM-L6-v2** encoder (384-d, uint8 per-channel ONNX) through hybrid lexical + semantic search.

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

## Neural retrieval & evaluation

`search_design_showcases.py` ranks the 950 showcases with a **hybrid** of lexical TF-IDF +
keyword boosts and a **fine-tuned semantic encoder**. The semantic layer is a fine-tuned
[`all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) (384-d),
exported to a ~23 MB **uint8 per-channel** ONNX model in `design_showcases/encoder/` and queried with
`onnxruntime` + `tokenizers` only — no torch at search time. Per-channel quantization keeps cosine
parity with the float checkpoint at ~0.99 (the earlier per-tensor int8 export lost several points of
Recall@5). The final score is `(1-w)·minmax(lexical) + w·minmax(semantic)` with `w = 0.7`, tuned on the
dev split. It applies to every query mode (search terms, `--3d`, `--category`, `--components`).

Broad-query detection is content-word based: a query only falls back to the six archetypes when it
has no specific content words left after removing stop words and generic design terms. This fixed an
earlier phrase-blacklist that hijacked specific queries (for example "3D bookshelf hover tilt") and
hid the real showcases.

The semantic layer is **optional**: install the runtime with `pip install -r requirements.txt`.
If `onnxruntime`/`tokenizers` or the encoder files are missing, search falls back to the pure
lexical pipeline, unchanged.

```bash
pip install -r requirements.txt        # numpy, scikit-learn, onnxruntime, tokenizers
python search_design_showcases.py "liquid glass refraction hero" --limit 3
python semantic_index.py rebuild       # regenerate design_embeddings.npy from the encoder
```

### Fine-tuning

The encoder is fine-tuned with Multiple-Negatives Ranking Loss on *query-style* anchors derived
from each showcase description, aligned to the index text `"{title}: {description}"`. Brand-only
titles (≤2 content words) are never used as anchors, which avoids the false-negative noise a naive
title-anchor recipe injects. One anchor per item per batch removes false in-batch negatives.
`train_retriever.ipynb` reproduces the full pipeline (train → evaluate → export → rebuild);
`eval/train_v2.py` is the script form. The export uses uint8 **per-channel** dynamic quantization
(`eval/export_encoder.py`), which holds ~0.99 cosine parity with the float checkpoint; the earlier
per-tensor int8 export measurably hurt Recall@5 and was replaced. The earlier `EmbeddingGemma-2`
branding was aspirational; the shipped 384-d index is MiniLM, which trains on CPU and exports to a
small ONNX encoder. EmbeddingGemma-2 (768-d, gated, GPU-only) remains an optional upgrade path.

**Prompt & UI-element coverage.** Every one of the 328 MotionSites showcases stores its verbatim
prompt in `showcases_meta.json` (`full_prompt`), alongside its interaction video and the UI elements
the prompt describes (visual engine, signature motion, layout/components, fonts, palette, stack).
A slug + prompt-text + video audit matched **328/328** with zero missing or mismatched items, and
`eval/ui_signature.py` extracts those UI elements deterministically. The descriptions the encoder
trains on are derived from these prompts, and the full prompt + UI blueprint is surfaced verbatim at
retrieval time (`--full` and the per-item source links). The encoder is a *retrieval* model — it ranks
the 950 reference designs for a query; it does not generate sites — so the indexed representation is
optimized for concept-level search, not for reproducing a prompt's every token.

### Before / after (held-out test split, 51 queries)

A hand-verified benchmark of 70 queries (`eval/benchmark.json`, 19 dev / 51 test) measures
P@1, Recall@5, MRR@10 and nDCG@5. The dev split selects the checkpoint and the hybrid weight;
the test split is reported once, untouched. All numbers below were re-measured from the deployed
pipeline with `eval/evaluate.py` and are stored in `eval/deployed_results.json`.

**Encoder quality** — pure semantic retrieval over `"title: description"` (test split):

| Model | P@1 | R@5 | MRR@10 | nDCG@5 |
| --- | --- | --- | --- | --- |
| base MiniLM (un-tuned) | 0.9216 | 0.8899 | 0.9477 | 0.8811 |
| fine-tuned float checkpoint | 0.9412 | 0.9330 | 0.9647 | 0.9122 |
| **shipped uint8 per-channel ONNX** | **0.9412** | **0.9183** | **0.9627** | **0.9072** |

The query-style recipe was selected over the notebook control on dev. Four further experiments were
run and **rejected** because dev got worse (the dev bar is the float checkpoint at nDCG@5 **0.934**,
R@5 **0.9254**):

- **Cleaned-text retrain** — over-stripped design tokens like WebGL and Three.js.
- **Hard-negative continue training** — dev R@5 fell 0.9254 → 0.9079.
- **UI-element anchors (Exp A)** — anchors distilled from the verbatim prompt's UI elements
  (`eval/ui_signature.py: ui_query`) trained against the unchanged `title: description` index.
  Dev nDCG@5 fell 0.934 → **0.9244** (train loss 3.27: the UI anchors sit far from the index text).
- **Enriched index (Exp B)** — the index text itself was augmented with a compact concept signature
  (engine + motion + layout) and `max_seq_length` raised 128 → 256. Even the *frozen* deployed encoder
  dropped to 0.9195 on the enriched index; the best retrained checkpoint reached only **0.9212**.

Both UI-element experiments fail for the same reason: engine/motion/layout terms are shared
boilerplate across many designs, so injecting them dilutes the distinctive description signal that
concept-level queries actually match. The shipped checkpoint remains the query-style fine-tune on
`title: description`; nothing was kept that did not generalize. The raw prompts and UI elements stay
available verbatim through `--full`, where they inform design without hurting ranking.

**Deployed search** — the full `search()` pipeline (test split):

| System | P@1 | R@5 | MRR@10 | nDCG@5 |
| --- | --- | --- | --- | --- |
| lexical only (semantic disabled) | 0.8235 | 0.8745 | 0.9020 | 0.8395 |
| committed baseline `dd30263` (before) | 0.8039 | 0.8647 | 0.8824 | 0.8275 |
| **hybrid, this session (after)** | **0.9804** | **0.9340** | **0.9902** | **0.9340** |

The gain comes from three fixes: the broad-query hijack no longer hides specific results, the
encoder ships per-channel uint8 instead of lossy per-tensor int8, and the hybrid weight was
re-validated on the clean dev split. The buggy baseline hybrid actually scored below lexical-only
on P@1 because it hijacked specific queries; the fix lifts the deployed search to P@1 0.9804 and
MRR@10 0.9902 on test, and P@1 1.0 / MRR@10 1.0 on dev.

Reproduce:

```bash
pip install torch sentence-transformers datasets accelerate onnx onnxscript
python eval/train_v2.py                                   # fine-tune, pick best dev checkpoint
python eval/export_encoder.py --checkpoint <best>         # bundle uint8 per-channel ONNX encoder
python semantic_index.py rebuild                          # regenerate the index
python eval/evaluate.py --systems lexical onnx stored base <best>
python eval/tune_hybrid.py                                # tune w on dev via the real search()
python eval/smoke_test.py                                 # end-to-end sanity checks
```

## Demonstration surfaces (local only)

To exercise the retrieval → design → lint loop end to end, a browsable gallery of the 950
showcases and three production landing pages were authored locally from retrieved blueprints
(a specialty-coffee subscription, a wavetable-synth dev tool, and a sleep-recovery smart ring).
Each was held to the library's quality floor: `unfslop lint` reports **0 findings**, every
interaction was exercised in a live browser (contrast ≥ 4.5:1, keyboard focus, reduced-motion,
responsive down to ~540 px, no horizontal overflow, no console errors), and they are **silent** —
visual motion only, no audio or haptic gimmicks.

These demonstration artifacts (the gallery server/page and the `sites/` landing pages) are
**intentionally kept out of this repository**. What ships here is the retrieval library, the
bundled ONNX encoder, the 950-item dataset, and the evaluation harness. 807 of the 950 dataset
items carry a looping interaction video, so the designs the encoder is trained on are the designs
you can actually watch through `--full` and the per-item source links.

## Attribution and licence

MIT for the code. The knowledge is an independent distillation of two Apache-2.0/MIT-licensed skills;
see `NOTICE.md`. Neither author endorses this project. If you want the full source material, install
the originals: `emilkowalski/skills` (`apple-design`) and `pbakaus/impeccable`.
