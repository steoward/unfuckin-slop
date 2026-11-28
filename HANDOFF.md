# Development handoff — work in progress

The goal is repeatable, source-quality UI construction, not a generic design prompt pack or a claim of perfect reproduction. The latest product adaptations still visibly regress toward ordinary model-generated layouts. This checkpoint is published at the user's request so work can continue in Codex; visual quality is **not accepted** yet.

## Implemented

- EmbeddingGemma 2 metadata and 384-token payload-chunk retrieval, multimodal windows, model/catalog fingerprints, and media hash validation. Legacy v1 indexes remain metadata-only. Rebuild for v2; `--text-cache` adds resumable text shards, `--text-only` explicitly excludes visual windows.
- `source_bundle.py`, `source_material.py`, `delivery_packet.py`: distinguish verified imported bundles, stored component snapshots, specifications, unresolved registry pointers, visual references and descriptions. Export original bytes, dependencies when supplied, SHA-256 and provenance without executing or installing retrieved code. `plan` exports by default; one blueprint owns page composition; extra slots are explicit. A plan's readiness is not a quality verdict.
- Rust CLI/install integration, Python regression tests, CI wiring and a payload-aware retrieval evaluator. LoRA checkpoints include resume integrity and coverage; no held-out improvement has been established.

## Evidence and limitations

| Trial | What was established | What was not |
| --- | --- | --- |
| OKTA/9 (`spin-product`) | Local reconstruction from MotionSites specification and original product video; interactive controls implemented. | User screenshot shows severe magenta/green striped video/canvas corruption; desktop/mobile upstream comparison and visual repair are unfinished. Do not claim a correct rendered product or exact page. |
| Creative Carousel 001 (`skiper-skiper50`) | Stored TSX SHA-256 matched the file used. Base Gemma pilot hybrid score 0.700, first among four candidates. Same-image local isolation vs integration had zero differing pixels in initial, pagination, and swipe states on desktop and mobile. Upstream interaction indices and 300ms transition matched. | Upstream used different art and a different mobile container width; the zero-pixel result is not an upstream comparison. Full coffee page design remains generic. Honor Skiper's applicable attribution/license terms. |
| Footwear v2 | `spin-product` first in bounded demo index, hybrid-relative score 1.0; actual licensed photo, crop/detail navigation and responsive interaction tests. | Not actual 360-degree rotation, not the original code or an upstream visual match; user reports generic design. |
| Coffee v2 | `coffee-rewards` first in bounded demo index, hybrid-relative score 0.9854; licensed photographs and tested selection/cart. | No verified original visual comparison; user reports generic design. |
| Audio v2 | Retrieved `cordex` specification (bounded index, hybrid-relative 0.952); photo preparation begun. | No finished new page. |

Local catalog inventory at this checkpoint: 979 design records (328 MotionSites, 651 Pixlpin), 9,735 components (37 Skiper, 9,698 21st.dev registry entries), 355 videos and 40 images. Registry entries generally lack locally resolved executable source. MotionSites prompts and URLs are not full page source. Pilot rankings use the base model and small candidate sets; scores are relative within a query/candidate set, not confidence or cosine. The full v2 index is incomplete. No comprehensive fine-tune or held-out base/adapter comparison has completed.

## Resume on the existing machine

The original local checkout was behind origin/main and contains private data. Changes were developed in the separate worktree `.slop-cache/next` inside the original checkout. Preserve that original worktree and the private catalog. Do not reset, clean, force-push, or publish its contents. The private Windows runtime and corpus are under `D:\unfslop-ft\embeddinggemma2`; the catalog with linked visual material is `drive-media\library`, media root `drive-media`, model `weights`, interpreter `runtime\Scripts\python.exe`. The isolated text-index copy is `.slop-cache/full-text-index` under the development worktree. These are local paths, not distributed dependencies.

Private local demos are under `.slop-cache/demos` in that worktree: `repro-spin`, `repro-component` (React + lockfile, verify.mjs, screenshots/comparison.json and provenance), `shoes-v2`, `coffee-v2`, and unfinished `audio-v2`. Existing servers used ports 8798 (static) and 4179 (component); restart if needed. The old SVG demos are rejected baselines. None of these assets, catalog payloads, model weights or private screenshots belong in GitHub. The prior Codex thread is `codex://threads/01a20d28-ed4a-72b2-8b82-8a9be30928b2`.

## Prioritized next work

1. **Fix OKTA/9 first.** Reproduce the user's striped magenta screenshot on the actual browser/GPU. Compare original MP4 frames decoded with FFmpeg to browser video and canvas pixels, inspect codec/pixel format and canvas capture path. Avoid retaining hundreds of full-resolution decoded frames in memory; test a bounded frame cache or all-intra seek fallback. Verify jacket silhouette, background, thumbnails, drag angles, hotspots, fonts and layout at desktop and mobile. The published gallery may not expose an executable full page; if so, distinguish original asset/precise spec comparison from upstream-page comparison. Do not relabel a video frame as a page screenshot.
2. **Make source reuse govern whole pages.** A single blueprint and packet export are necessary but not sufficient. Add structured composition and motion contracts grounded in actual screenshots, full prompts and executable sources, with explicit element-to-file mappings, layout/viewport states and compatibility constraints. Resolve and reuse whole authorized page implementations where available. Prefer coherent source-compatible sets over a collection of unrelated high-scoring components. Require a record of which files/assets actually enter the build, not just the retrieval packet. A generic shell around a faithful carousel is still a failure.
3. **Resolve source availability.** Inventory permitted 21st.dev registry source access, dependencies, styles and licenses; cache only authorized snapshots with revision and hashes. Link authorized MotionSites visual assets to exact IDs with media manifests. Avoid silently replacing missing photography or motion with generic SVG. Never strip required third-party attribution; use an authorized alternative or license if a clean presentation requires it. Remote URLs alone do not establish rights or completeness.
4. **Finish the full v2 index.** Use the private copy and resumable text shards, check throughput, then cover all local visual windows with a matching checkpoint/cache. Report actual record/chunk/window counts, missing assets and failures. No model retraining just to make the index complete. Evaluate retrieval on multiple unseen briefs with the full candidate pool, reporting metadata-only, chunk, lexical and hybrid ablations separately.
5. **Evaluate before fine-tuning.** Split by reference ID and near-duplicate families before creating training pairs; reserve independently authored paraphrases and visual queries for dev/test. Compare base vs existing adapter on identical held-out queries and pools, report P@1, R@5, MRR and visual retrieval plus coverage. Existing smoke checkpoints may be useful for mechanics, not a proven improvement; changed training splits invalidate exact-resume signatures. Train only if a measured gap merits it, with a GPU and explicit budget.
6. **Prove generalization and execution.** Rebuild footwear, coffee and audio around retrieved composition, authorized assets and real motion; include varied new briefs selected without pre-pinning a reference. Record query, candidate pool, model fingerprint, score kind, selected materials/hashes, integration mapping, dependency lockfile and state screenshots. Test at desktop/mobile, keyboard/touch and motion states. Compare against the actual source and a plain-agent baseline; use an independent reviewer and record failures. User's latest feedback: both revised product sites are good but noticeably return to GPT's ordinary taste.
7. **Release gate.** Separate retrieval, delivery, execution and visual fidelity. Run Rust/Python/integration/CI, but do not interpret green tests as a visual pass. The current publication is a development checkpoint authorized by the user, not a completed product. Future claims of exceptional quality require independent comparison across multiple unpinned briefs and sources.

## Verification commands

```sh
python -m unittest discover -s eval -p 'test_*.py'
cargo test --locked
cargo build --locked --bin unfslop
# Install into a new temporary directory and exercise its binary:
cargo run --locked --bin unfslop -- install --dir PATH_TO_TEMP_SKILL
python eval/verify_design_packet.py PATH_TO_TEMP_SKILL/bin/unfslop
python semantic_index.py rebuild --text-only --text-cache PATH_TO_PRIVATE_SHARDS
python semantic_index.py rebuild-components --text-only --text-cache PATH_TO_PRIVATE_SHARDS
# For multimodal rebuild omit --text-only and provide --visual-cache.
```

On Windows use `unfslop.exe` and set `UNFSLOP_PYTHON`, `UNFSLOP_LIBRARY_DATA`, `UNFSLOP_MEDIA_ROOT`, `UNFSLOP_MODEL` and, when evaluating a trained adapter, `UNFSLOP_ADAPTER`. Use a fresh private destination for exports. Remote CI must be checked after the checkpoint is pushed.
