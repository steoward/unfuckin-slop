# Unfuckin-Slop

Search a private library of UI prompts, components, screenshots and motion references using **EmbeddingGemma 2**. The CLI can retrieve by text or screenshot, identify matching moments in local videos, and suggest material for each part of a page. The coding agent opens the references and applies specific visual decisions to the product.

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

For a large media collection, pass `--visual-cache PATH_TO_PRIVATE_CACHE` to `semantic_index.py rebuild`. A rerun with the same checkpoint and cache can reuse completed assets by content hash.

## Use

```sh
unfslop plan "Industrial product site, photographic hero and interactive process walkthrough"
unfslop library "motion-led product carousel"
unfslop library "strong typographic hierarchy" --reference screenshot.png
unfslop library --record 3d-character-studio --record skiper-skiper48
unfslop context "audit a modal for keyboard and focus behavior"
unfslop lint src/
```

`library` supports paging and filters on provider, pool and category. `plan` selects a blueprint and material for each section. Repeat `--section NAME=QUERY` to set the sections or add `--full` to include full selected records. An exact match opens the catalog. Search reports `gemma2_text`, `gemma2_multimodal`, or lexical fallback. A multimodal match with local video evidence includes a path and the time of the strongest matching window. Search treats every local video as consecutive eight-sample windows at one frame per second.

## Fine-tune

```sh
python train_gemma2.py --output PATH_TO_CHECKPOINTS --batch-size 4
```

The trainer uses contrastive LoRA with all imported text records and available local visual assets. It tokenizes long source payloads into chunks, samples videos across their timeline, and writes resumable checkpoints with counts. Use `--resume PATH_TO_STEP` to resume. Point `UNFSLOP_ADAPTER` at the chosen checkpoint and rebuild both indexes before evaluating. A GPU is recommended for the full corpus. See [Google's EmbeddingGemma 2 fine-tuning guide](https://gemma.ai/models/embeddinggemma/fine-tuning-multimodal/).

Project code is [MIT licensed](LICENSE). See [credits and third-party material](NOTICE.md).
