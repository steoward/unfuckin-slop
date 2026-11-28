# Unfuckin-Slop

Search a private library of UI prompts, components, screenshots and motion references using **EmbeddingGemma 2**. The CLI retrieves by text or screenshot, identifies matching moments in local videos, and exports selected original material with provenance. A build plan is anchored to one page reference rather than a generic landing-page template. The coding agent still has to integrate or reconstruct the reference and verify the rendered result. This is a work in progress, not a guarantee of source-level visual quality. See [development handoff](HANDOFF.md) for current evidence, limitations and next steps.

## Set up a private library

Install Python 3.12 or 3.13, Rust and FFmpeg. Install matching PyTorch and Torchvision builds for your device, then run:

```sh
python -m pip install -r requirements.txt
python prepare_catalog.py --prompts PATH_TO_PROMPTS --output design_showcases
python semantic_index.py rebuild
python semantic_index.py rebuild-components
cargo run --locked --release --bin unfslop -- install --agent codex
```

The importer reads `motionsites-free-prompts.txt`, `skiper-ui-free-prompts.txt` and `21st-dev-free-prompts.txt`. To preserve existing IDs and add existing Pixlpin metadata, pass `--archive PATH_TO_PRIVATE_CATALOG`. For media, pass `--media-manifest PATH_TO_JSONL --media-root PATH_TO_ASSETS`. Media rows may attach an asset to an existing ID or add a CollectUI/Pixlpin reference using an authorized asset. Each line contains `id`, `path` relative to the media root, and `rights`. For a new record, also include `title`, `source_url`, `description` and optionally `category` and `type`. The importer records local assets separately from remote video references. A media row may include an inline `annotation` report from Gemini or another reviewer. Use `catalog_id`, `asset_sha256`, `provider`, `model_display_name` and an `annotation` object with `summary`, `composition`, `palette`, `observed_motion` and optional timestamped `moments`. The importer checks the asset hash and video duration. The library indexes the visual description and returns the model provenance with matching moments. Keep prompt payloads and media private and follow the original sources' terms.

Set `UNFSLOP_LIBRARY_DATA` to the absolute catalog directory when running the installed CLI, and `UNFSLOP_MEDIA_ROOT` if media is stored separately. Set `UNFSLOP_PYTHON` to the Python executable with the installed dependencies. The runtime loads the pinned official Google checkpoint on demand. `UNFSLOP_MODEL` can point to a local copy. The index stores a fingerprint of its model adapter and catalog, and reports when changes require a rebuild.

Rebuild both indexes after upgrading the runtime. The version 2 index includes embeddings of the full stored prompt or code in 384-token chunks, as well as catalog descriptions and visual windows. Queries can match details beyond the title or summary. Local model weights, adapter weights and source payloads are fingerprinted; changed data requires rebuilding rather than silently serving a mismatched index.

For a large media collection, pass `--visual-cache PATH_TO_PRIVATE_CACHE` to `semantic_index.py rebuild`. A rerun with the same checkpoint and cache can reuse completed assets by content hash.

For a staged rebuild, use `--text-cache PATH_TO_PRIVATE_CACHE` to save resumable, content-addressed text shards. `--text-only` deliberately omits visual windows; it is useful for establishing text retrieval coverage first, not a substitute for the multimodal index. A subsequent multimodal rebuild must use the full media catalog. Keep cache and delivery directories private.

## Use

```sh
unfslop plan "Industrial product site, photographic hero and interactive process walkthrough"
unfslop library "motion-led product carousel"
unfslop library "strong typographic hierarchy" --reference screenshot.png
unfslop library "drag stacked cards" --pool components --full
unfslop library "drag stacked cards" --pool components --limit 1 --export-dir NEW_PRIVATE_DIRECTORY
unfslop library --record 3d-character-studio --record skiper-skiper48
unfslop context "audit a modal for keyboard and focus behavior"
unfslop lint src/
```

`library` supports paging and filters on provider, pool and category. Add `--full` to receive original stored payloads and named source files directly. `plan` selects one principal blueprint, preserves its composition and includes complete selected records. Supplementary sections are explicit (`--section NAME=QUERY`); `plan --full` expands alternatives. Exact IDs open the catalog without loading the model. Search reports `gemma2_text`, `gemma2_multimodal`, or lexical fallback; hybrid-relative ranking scores are not raw cosine or confidence. Screenshot retrieval ranks indexed visual evidence directly. A match with local video evidence includes the original path, the strongest matching window and a generated contact sheet when full material is requested. Search treats every local video as consecutive eight-sample windows at one frame per second.

`plan` exports selected material by default into a new directory under `UNFSLOP_DELIVERY_ROOT` (defaults to `.deliveries` inside the private catalog). The manifest records source, query/backend, scores, file hashes, dependencies and missing evidence. `--export-dir` chooses a new destination explicitly; `plan --no-export` inspects without writing. `library --export-dir` exports full matching records. Export does not execute code, install packages, authorize reuse or establish rendering fidelity. Keep the resulting packet out of public repositories.

Every entry reports its delivery tier: `source_bundle`, `source_snapshot`, `build_specification`, `registry_pointer`, `visual_reference` or `description_only`. A full entry provides `delivery.payload`, SHA-256 of the stored payload, and any named `delivery.files`. `inspection` verifies the local visual asset against its recorded SHA-256 and supplies a still or contact sheet. Set `UNFSLOP_REFERENCE_CACHE` to choose the private preview cache directory. These checks establish faithful delivery of the stored material, not that the result is a complete licensed build or visually identical to a source site. EmbeddingGemma 2 ranks records; original material remains external to its weights.

To add original implementation files that you are authorized to store and reuse, supply `prepare_catalog.py --source-manifest PATH --source-root DIRECTORY` along with the usual importer arguments. Each JSONL entry identifies an existing record by `id` and exact `source_url`, declares `revision`, `license`, `rights`, optional `dependencies` and a list of `files`. A file has a root-relative `path`, intended project-relative `target`, `kind` (`text` or `asset`) and optional expected `sha256`. The importer hashes every file and records provenance. Set `UNFSLOP_SOURCE_ROOT` at runtime to locate those private files; full retrieval verifies all hashes before returning source text and asset paths. The source manifest is a declaration of rights, not independent legal verification. Do not scrape or redistribute restricted source material.

## Fine-tune

```sh
python train_gemma2.py --output PATH_TO_CHECKPOINTS --batch-size 4
```

The trainer uses contrastive LoRA with imported text records and available local visual assets. It tokenizes long source payloads into chunks, samples videos across their timeline, and writes resumable checkpoints with counts. Use `--resume PATH_TO_STEP` to resume a matching corpus/configuration. Point `UNFSLOP_ADAPTER` at the chosen checkpoint and rebuild both indexes before evaluating. A GPU is recommended for the full corpus. The current smoke runs prove checkpoint mechanics, not a gain over the base model. Before a full training run, make disjoint training and evaluation inputs and compare the adapter against the base model on held-out queries and visual references. See [Google's EmbeddingGemma 2 fine-tuning guide](https://gemma.ai/models/embeddinggemma/fine-tuning-multimodal/).

Project code is [MIT licensed](LICENSE). See [credits and third-party material](NOTICE.md).
