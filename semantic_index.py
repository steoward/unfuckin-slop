"""EmbeddingGemma 2 retrieval over private text and visual catalog assets."""
from functools import cache
import hashlib
import json
import os
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import NamedTuple

import numpy as np

from visual_annotations import annotation_text

MODEL_ID = "google/embeddinggemma-2"
REVISION = "f9972ac22e696a105c482202646979e33e4b5a1e"
DIM = 768
VISUAL_WINDOW_SECONDS = 8
VISUAL_CACHE_VERSION = 2
DATA_DIR = Path(os.environ.get("UNFSLOP_LIBRARY_DATA", Path(__file__).resolve().parent / "design_showcases"))
MEDIA_DIR = Path(os.environ.get("UNFSLOP_MEDIA_ROOT", DATA_DIR / "media"))


def model_key():
    adapter = os.environ.get("UNFSLOP_ADAPTER")
    if not adapter:
        return REVISION
    files = sorted(Path(adapter).rglob("adapter_model.safetensors"))
    if not files:
        raise FileNotFoundError(f"No adapter weights in {adapter}")
    checksum = hashlib.sha256(REVISION.encode())
    for path in files:
        with path.open("rb") as stream:
            checksum.update(hashlib.file_digest(stream, "sha256").digest())
    return checksum.hexdigest()


@cache
def load_encoder(vision=False, adapter=True):
    from sentence_transformers import SentenceTransformer
    import torch

    source = os.environ.get("UNFSLOP_MODEL", MODEL_ID)
    config = {"audio_config": None}
    if not vision:
        config["vision_config"] = None
    device = os.environ.get("UNFSLOP_DEVICE") or ("cuda" if torch.cuda.is_available() else "cpu")
    if device == "cpu":
        torch.set_num_threads(min(6, os.cpu_count() or 1))
    bf16 = device.startswith("cuda") and torch.cuda.is_bf16_supported(including_emulation=False)
    model = SentenceTransformer(
        source, revision=REVISION if source == MODEL_ID else None, device=device,
        config_kwargs=config, model_kwargs={"dtype": "bfloat16" if bf16 else "float32"},
    )
    if adapter and (path := os.environ.get("UNFSLOP_ADAPTER")):
        model.load_adapter(path)
    return model


def query_vectors(queries, reference=None):
    model = load_encoder(vision=reference is not None)
    if reference is None:
        return model.encode_query(queries, normalize_embeddings=True, show_progress_bar=False)
    from PIL import Image

    with Image.open(reference) as image:
        pixels = image.convert("RGB")
    return model.encode(
        [{"text": model.prompts["query"] + query, "image": pixels} for query in queries],
        normalize_embeddings=True, show_progress_bar=False,
    )


def canonical_rows(pool):
    return json.loads((DATA_DIR / f"{pool}_meta.json").read_text(encoding="utf-8"))


def document_text(row):
    tags = ", ".join(row.get("tags") or [])
    return "\n".join(filter(None, (row["title"], row.get("category"), row.get("description"), tags, annotation_text(row))))


def row_digest(rows):
    values = [(row["id"], document_text(row),
               [(asset["kind"], asset["path"], asset["sha256"]) for asset in row.get("media", [])])
              for row in rows]
    return hashlib.sha256(json.dumps(values, ensure_ascii=False).encode()).hexdigest()


class Index(NamedTuple):
    text: np.ndarray
    visual: np.ndarray
    owners: np.ndarray
    asset_indices: np.ndarray
    starts: np.ndarray

    def rank(self, indices, vector):
        text = self.text[indices] @ vector
        best = {}
        if self.visual.size:
            for slot, score in enumerate(self.visual @ vector):
                owner = int(self.owners[slot])
                if owner not in best or score > best[owner][0]:
                    best[owner] = (float(score), int(self.asset_indices[slot]), float(self.starts[slot]))
        return text, best


def index_path(pool):
    return DATA_DIR / f"{pool}_gemma2.npz"


@cache
def open_index(pool):
    path = index_path(pool)
    if not path.is_file():
        return None
    with np.load(path, allow_pickle=False) as value:
        if value["model"].item() != model_key() or value["corpus"].item() != row_digest(canonical_rows(pool)):
            raise ValueError(f"{path.name} does not match the configured checkpoint or catalog; rebuild it")
        return Index(*(value[name] for name in Index._fields))


def media_path(asset):
    root = MEDIA_DIR.resolve()
    path = (root / asset["path"]).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise FileNotFoundError(f"Media file missing from {root}: {asset['path']}")
    return path


def media_windows(asset):
    """Yield a still image or consecutive windows at one sampled frame per second."""
    from PIL import Image

    path = media_path(asset)
    if asset["kind"] == "image":
        with Image.open(path) as image:
            yield 0.0, {"image": image.convert("RGB")}
        return
    with TemporaryDirectory(prefix="unfslop-frames-") as folder:
        directory = Path(folder)
        subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(path), "-an",
             "-vf", "fps=1:round=up,scale=w=768:h=768:force_original_aspect_ratio=decrease",
             "-start_number", "0", str(directory / "%09d.jpg")],
            check=True, capture_output=True,
        )
        frames = sorted(directory.glob("*.jpg"))
        if not frames:
            raise ValueError(f"No frames decoded: {path}")
        for start in range(0, len(frames), VISUAL_WINDOW_SECONDS):
            images = []
            for frame in frames[start:start + VISUAL_WINDOW_SECONDS]:
                with Image.open(frame) as image:
                    images.append(image.convert("RGB"))
            yield float(start), {"video": images}


def save_index(path, **arrays):
    with NamedTemporaryFile(dir=path.parent, suffix=".npz", delete=False) as stream:
        temporary = Path(stream.name)
    try:
        np.savez(temporary, **arrays)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def encode_asset(model, asset, checkpoint, cache_dir):
    cached = None
    if cache_dir is not None:
        path = media_path(asset)
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if digest != asset["sha256"]:
            raise ValueError(f"Media changed since catalog import: {path}")
        cache_key = f"{VISUAL_CACHE_VERSION}-{checkpoint}-{asset['kind']}-{digest}"
        cached = cache_dir / f"{cache_key}.npz"
        if cached.is_file():
            with np.load(cached, allow_pickle=False) as arrays:
                return arrays["starts"], arrays["visual"]
    starts, visual = [], []
    for start, inputs in media_windows(asset):
        starts.append(start)
        visual.append(model.encode(inputs, normalize_embeddings=True, show_progress_bar=False))
    starts, visual = np.asarray(starts), np.asarray(visual, dtype=np.float32)
    if cached is not None:
        save_index(cached, starts=starts, visual=visual)
    return starts, visual


def build_index(pool, batch_size, visual_cache=None):
    rows = canonical_rows(pool)
    media = [(owner, index, asset) for owner, row in enumerate(rows)
             for index, asset in enumerate(row.get("media", []))]
    checkpoint = model_key()
    model = load_encoder(vision=bool(media))
    if visual_cache is not None:
        visual_cache.mkdir(parents=True, exist_ok=True)
    visual, owners, asset_indices, starts = [], [], [], []
    for completed, (owner, index, asset) in enumerate(media, 1):
        times, vectors = encode_asset(model, asset, checkpoint, visual_cache)
        visual.extend(vectors)
        starts.extend(times)
        owners.extend([owner] * len(times))
        asset_indices.extend([index] * len(times))
        if completed % 25 == 0 or completed == len(media):
            print(f"Visual assets: {completed}/{len(media)} ({len(visual)} windows)", flush=True)
    text = model.encode_document(
        [document_text(row) for row in rows], normalize_embeddings=True,
        batch_size=batch_size, show_progress_bar=True,
    )
    path = index_path(pool)
    save_index(path, model=checkpoint, corpus=row_digest(rows), text=text,
               visual=np.asarray(visual, dtype=np.float32).reshape(-1, DIM),
               owners=owners, asset_indices=asset_indices, starts=starts)
    print(f"{path}: {len(rows)} text records, {len(visual)} visual windows", flush=True)


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("rebuild", "rebuild-components"))
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--visual-cache", type=Path, help="Reuse previously encoded assets during a rebuild")
    args = parser.parse_args()
    build_index("components" if args.operation == "rebuild-components" else "showcases",
                args.batch_size, args.visual_cache)


if __name__ == "__main__":
    main()
