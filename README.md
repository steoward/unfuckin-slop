# Unfuckin-Slop

Autonomous UI & Kinetic Design System for Coding Agents: Production-grade component library, model-grounded inspiration, and anti-slop quality floor.

Two of the best frontend design skills, **Apple Design** (Emil Kowalski, distilled from Apple's
WWDC interface talks) and **Impeccable** (Paul Bakaus, Apache-2.0), fused into **30 atom cards** and
served on demand by a **standalone Rust binary** — paired with a curated 950 UI design system showcase library
(622 Pixlpin visual showcases + 328 MotionSites full prompt blueprints) retrieved by a fine-tuned
**all-MiniLM-L6-v2** encoder (384-d, uint8 per-channel ONNX) through hybrid lexical + semantic search.
A second pool (`--pool components`) adds **9,735 UI component code prompts** (9,698 from 21st.dev +
37 from skiper.ui) with verbatim implementations and install commands, searched by the same encoder.

For a new screen, `unfslop design` retrieves design evidence from the local model and pairs it with Apple Design and Impeccable guidance. The coding agent chooses the composition. For a review or repair, `unfslop context` serves focused craft guidance.

## Quick start

```bash
python -m pip install -r requirements.txt   # in your Python environment
cargo build --release          # builds unfslop
target/release/unfslop design "field-recording archive with a track list and audio player"
target/release/unfslop doctor
target/release/unfslop context "settings page with destructive actions"
```

Use the newly built CLI or the one in a current CI bundle. The historical Windows executable tracked under `skills/unfuckin-slop/bin/` predates the `design` command. If you move the CLI alone onto PATH, point `UNFSLOP_DESIGN_LIBRARY` at the checkout or the installed `design-library/`.

### Install as an agent skill

To use the tested binary without building it, open the successful Rust CI run for your revision and download the `unfuckin-slop-<OS>-<ARCH>` artifact for your machine. Unzip it, then extract the enclosed `.tar.gz` into your agent’s skills directory. The archive preserves the executable permissions on Unix. To build and install from source, run the commands below with your freshly built CLI on PATH.

```bash
unfslop install                  # → .claude/skills/unfuckin-slop
unfslop install --user           # → ~/.claude/skills/unfuckin-slop
unfslop install --dir path/to/skills/unfuckin-slop
```

That writes `SKILL.md`, all 30 cards, `NOTICE.md`, and a copy of the binary at `bin/unfslop`, so the
skill keeps working on a machine with no Cargo toolchain. Build the CLI from this checkout before installing to pick up the current router and embedded guide. The installer copies the reference engine, catalogs and ONNX model into `design-library/` when run from a checkout build or a full bundle. Install `design-library/requirements.txt` in your Python environment. `UNFSLOP_PYTHON` selects a specific interpreter and `UNFSLOP_DESIGN_LIBRARY` can point a binary-only installation at an existing checkout. Any SKILL.md-compatible agent can use it
(Claude Code, Codex, Cursor, Copilot, and friends); point it at the folder.

For this repository itself, the skill is already in `skills/unfuckin-slop/`. Agents that scan
`.claude/skills` need the install step.

## Commands

| Command | What it does |
| --- | --- |
| `unfslop design "<brief>" [--pool components]` | JSON with up to three catalog references, retrieval status, and one complete Apple and Impeccable card each. | 
| `unfslop context "<task>"` | Rank task-specific craft cards for a repair, review or deeper follow-up. |
| `--budget N` | Token ceiling for the pack. Default 2000. |
| `--limit N` | Card ceiling. Default 6. |
| `--mode M` | Force a mode: `build`, `motion`, `gesture`, `critique`, `polish`, `system`, `a11y`, `native`, `inspire`. |
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
`color`, `motion`, `states`, `copy`, `a11y`, `performance`, `critique`, `polish`, `system`, `inspiration`.

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

`always: true` marks the craft floor, which is placed after the first mode card when it fits, or first when the mode supplies no cards.

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

- **Standalone CLI.** Cargo resolves the Rust dependencies at build time. The built CLI runs independently of Python and the optional showcase index.
- **Embedded cards with a disk override.** `build.rs` bakes the cards into the binary so it works
  anywhere; if `UNFUCKIN_SLOP_HOME` or a `cards/` directory sits next to the binary or the cwd, that
  wins, so editing a card is a rebuild-free operation.
- **Budget is estimated, not tokenized.** Four characters per token keeps the tool instant and errs on
  the safe side. The pack never pads to fill the budget: if a mandated card does not fit, it stops.
- **Relevance is thresholded.** Extras must score at least 25% of the best match, so a big budget
  cannot smuggle in weak material.
- **Source checks and rendered checks.** Lint reports recognizable patterns. Use the rendered surface for computed contrast, keyboard navigation, responsive layout and recovery behavior.

## Verify

```bash
cargo test                     # unit & integration tests
cargo build --release          # builds standalone unfslop
target/release/unfslop context "spring sheet snap" --budget 1200
target/release/unfslop lint fixtures; echo "exit=$?"
```

## Autonomous UI & Kinetic Design System

Unfuckin-Slop operates completely self-contained with **zero external MCP dependencies**.

### Workflow

1. Identify the main action, surface intent and whether the request is a build, refinement or review. Inspect the incumbent UI and its actual content.
2. For new design work, run `unfslop design` with a specific subject and interaction. Review the catalog text or linked media, sketch two candidate compositions with real content, and choose the one that best serves the primary task.
3. Use the accompanying craft lenses to refine the chosen composition. Pull related cards for deeper decisions, or use `unfslop context` directly for focused repairs. If retrieval falls back, the packet reports the backend or the reason it could not retrieve references.
4. Run lint over changed web paths, then exercise the primary flow, keyboard interaction and relevant recovery at supported sizes. Report the checks you could perform.

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

# Search the separate 9,735-component code library (21st.dev + skiper.ui)
python search_design_showcases.py --pool components "gooey liquid effect" --limit 3
python search_design_showcases.py --pool components "card swipe carousel" --full   # verbatim code
python search_design_showcases.py --pool components --3d --category Background
```

### What it provides:
- **Production UI Component Tokens (`--components`)**: Ready-to-use button primitives (glow CTA, ghost), Bento card surface elevations, floating pill navigation bars, and radial atmosphere lighting tokens.
- **Visual hierarchy & layout breakdown**: Surface contrast, spatial elevation, typography scale, and color systems.
- **Physical Spring & Motion Parameters**: Exact `stiffness`, `damping`, durations, and CSS cubic-bezier curves.
- **Direct Video Reference**: Direct link to the high-frame-rate interaction video.

Use a reference to answer a specific design question, then verify the resulting behavior in the product.

## Visual comparison

Open [the standalone comparison](eval/design-pilot.html) in a browser to run four prototypes at desktop and phone widths. Two identical briefs were each implemented with selected craft cards and with the reference-grounded workflow. A blinded reviewer preferred the hybrid archive for identity but the cards-only archive for ease of choosing a recording. For the editorial rights desk the reviewer preferred the hybrid overall, while the cards-only table kept clearer mobile column labels. These are two exploratory pairs. Retrieval metrics below measure finding records, a separate outcome.

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

### Component library (`--pool components`)

A second, separate pool holds **9,735 UI component code prompts** — 9,698 community components from
[21st.dev](https://21st.dev/community/components) and 37 from [skiper.ui](https://skiper-ui.com) —
parsed into `design_showcases/components_meta.json` and indexed with the **same** fine-tuned encoder
(`design_showcases/component_embeddings.npy`, `python semantic_index.py rebuild-components`). These
sources ship verbatim implementations and npm install commands rather than interaction video, so
component results carry tags / install metadata and surface the full code prompt through `--full`.
The pool is kept apart from the 950 full-design showcases so the design benchmark and design search
stay clean; `search_components()` reuses the same hybrid lexical + semantic ranking (`w = 0.7`).

On **28 natural-language probes** (descriptive and name-based, e.g. "gooey liquid effect on elements",
"card swipe carousel with stacking and gestures") the deployed encoder retrieves the target component
in the top 5 every time — **R@5 1.0, P@1 0.9286, MRR@10 0.9643** (the two rank-2 cases are near-duplicate
siblings: a murmuration-boids vs murmuration-wordmark, and a 21st.dev mirror of skiper89). The designs-only
fine-tune generalizes to these component prompts without any component-specific training (see Exp C).

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

The query-style recipe was selected over the notebook control on dev. Five further experiments were
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
- **Combined designs + components (Exp C)** — continued training on the 950 designs *plus* the 9,735
  component prompts (10,685 pairs, 91% components). Design dev nDCG@5 fell 0.934 → **0.9274** (A_desc14)
  / **0.9273** (B_desc20): the much larger component corpus dilutes the distinctive design signal.
  Component retrieval was **identical** to the designs-only encoder (P@1 0.9286, R@5 1.0, MRR@10 0.9643
  on 28 probes) — the query-style fine-tune already generalizes to the new component prompts, so the
  combined training bought nothing for components and cost design accuracy. Rejected; the shipped
  encoder stays the designs-only `queryv2_phase2`, and the component pool is indexed with it.

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
python semantic_index.py rebuild                          # regenerate the design index
python semantic_index.py rebuild-components               # regenerate the 9,735-component index
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
