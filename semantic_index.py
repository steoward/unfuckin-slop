"""EmbeddingGemma 2 retrieval over private text and visual catalog assets."""
from functools import cache
import hashlib
from itertools import islice
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
INDEX_VERSION = 2
PAYLOAD_WINDOW_TOKENS = 384
VISUAL_WINDOW_SECONDS = 8
VISUAL_CACHE_VERSION = 2
DATA_DIR = Path(os.environ.get("UNFSLOP_LIBRARY_DATA", Path(__file__).resolve().parent / "design_showcases"))
MEDIA_DIR = Path(os.environ.get("UNFSLOP_MEDIA_ROOT", DATA_DIR / "media"))


def checkpoint_files(root, files):
    entries = []
    for path in sorted(files):
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        entries.append((path.relative_to(root).as_posix(), digest))
    return hashlib.sha256(json.dumps(entries).encode()).hexdigest()


def model_key(adapter=True):
    source = os.environ.get("UNFSLOP_MODEL") or MODEL_ID
    base = REVISION
    if source != MODEL_ID:
        root = Path(source).resolve()
        files = [path for path in root.rglob("*") if path.is_file()
                 and not {".git", ".cache"}.intersection(path.relative_to(root).parts)]
        if not files:
            raise FileNotFoundError(f"No local model checkpoint files in {root}")
        base = checkpoint_files(root, files)
    if not adapter or not (location := os.environ.get("UNFSLOP_ADAPTER")):
        return base
    root = Path(location).resolve()
    files = [root / name for name in ("adapter_model.safetensors", "adapter_model.bin", "adapter_config.json")
             if (root / name).is_file()]
    if not any(path.name.startswith("adapter_model.") for path in files):
        raise FileNotFoundError(f"No adapter weights in {root}")
    return hashlib.sha256(f"{base}:{checkpoint_files(root, files)}".encode()).hexdigest()


@cache
def load_encoder(vision=False, adapter=True):
    from sentence_transformers import SentenceTransformer
    import torch

    source = os.environ.get("UNFSLOP_MODEL") or MODEL_ID
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


def payload_chunks(tokenizer, payload):
    tokens = tokenizer.encode(payload, add_special_tokens=False, truncation=False, verbose=False)
    for offset in range(0, len(tokens), PAYLOAD_WINDOW_TOKENS):
        yield tokenizer.decode(tokens[offset:offset + PAYLOAD_WINDOW_TOKENS], skip_special_tokens=True)


def index_digest(rows):
    checksum = hashlib.sha256(f"{INDEX_VERSION}:{PAYLOAD_WINDOW_TOKENS}:{row_digest(rows)}".encode())
    for row in rows:
        checksum.update(hashlib.sha256((row.get("full_prompt") or "").encode()).digest())
    return checksum.hexdigest()


class Index(NamedTuple):
    text: np.ndarray
    visual: np.ndarray
    owners: np.ndarray
    asset_indices: np.ndarray
    starts: np.ndarray
    chunks: np.ndarray | None = None
    chunk_owners: np.ndarray | None = None

    def rank_text(self, indices, vector):
        text = self.text[indices] @ vector
        if self.chunks is not None and self.chunks.size:
            best_chunks = np.full(len(self.text), -np.inf, dtype=text.dtype)
            np.maximum.at(best_chunks, self.chunk_owners, self.chunks @ vector)
            text = np.maximum(text, best_chunks[indices])
        return text

    def rank(self, indices, vector):
        text = self.rank_text(indices, vector)
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
        version = value["version"].item() if "version" in value else 1
        if version not in (1, INDEX_VERSION):
            raise ValueError(f"{path.name} has an unsupported index version; rebuild it")
        rows = canonical_rows(pool)
        corpus = row_digest(rows) if version == 1 else index_digest(rows)
        if value["model"].item() != model_key() or value["corpus"].item() != corpus:
            raise ValueError(f"{path.name} does not match the configured checkpoint or catalog; rebuild it")
        fields = Index._fields[:5] if version == 1 else Index._fields
        return Index(*(value[name] for name in fields))


def media_path(asset):
    root = MEDIA_DIR.resolve()
    path = (root / asset["path"]).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise FileNotFoundError(f"Media file missing from {root}: {asset['path']}")
    return path


def media_windows(asset):
    """Yield a still image or consecutive windows at one sampled frame per second."""
    yield from decode_media_windows(asset["kind"], verified_media_path(asset))


def verified_media_path(asset):
    path = media_path(asset)
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest != asset["sha256"]:
        raise ValueError(f"Media changed since catalog import: {path}")
    return path


def decode_media_windows(kind, path):
    from PIL import Image

    if kind == "image":
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
    path = verified_media_path(asset)
    cached = None
    if cache_dir is not None:
        cache_key = f"{VISUAL_CACHE_VERSION}-{checkpoint}-{asset['kind']}-{asset['sha256']}"
        cached = cache_dir / f"{cache_key}.npz"
        if cached.is_file():
            with np.load(cached, allow_pickle=False) as arrays:
                return arrays["starts"], arrays["visual"]
    starts, visual = [], []
    for start, inputs in decode_media_windows(asset["kind"], path):
        starts.append(start)
        visual.append(model.encode(inputs, normalize_embeddings=True, show_progress_bar=False))
    starts, visual = np.asarray(starts), np.asarray(visual, dtype=np.float32)
    if cached is not None:
        save_index(cached, starts=starts, visual=visual)
    return starts, visual


def encode_payloads(model, rows, batch_size):
    entries = ((owner, chunk) for owner, row in enumerate(rows)
               if (payload := row.get("full_prompt"))
               for chunk in payload_chunks(model.tokenizer, payload))
    embeddings, owners = [], []
    while batch := list(islice(entries, batch_size)):
        batch_owners, texts = zip(*batch)
        vectors = model.encode_document(list(texts), normalize_embeddings=True,
                                        batch_size=batch_size, show_progress_bar=False)
        embeddings.append(np.asarray(vectors, dtype=np.float32))
        owners.extend(batch_owners)
    chunks = np.concatenate(embeddings) if embeddings else np.empty((0, DIM), dtype=np.float32)
    return chunks, np.asarray(owners, dtype=np.intp)


def build_index(pool, batch_size, visual_cache=None, *, text_only=False, text_cache=None):
    if batch_size < 1:
        raise ValueError("Batch size must be positive")
    rows = canonical_rows(pool)
    media = [(owner, index, asset) for owner, row in enumerate(rows)
             for index, asset in enumerate(row.get("media", []))]
    if text_only:
        media = []
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
    if text_cache is None:
        text = model.encode_document(
            [document_text(row) for row in rows], normalize_embeddings=True,
            batch_size=batch_size, show_progress_bar=True,
        )
        chunks, chunk_owners = encode_payloads(model, rows, batch_size)
    else:
        # Persist bounded, content-addressed shards. A cancelled run can restart
        # without re-encoding completed rows; changing any input invalidates it.
        text_cache.mkdir(parents=True, exist_ok=True)
        texts, payloads, payload_owners = [], [], []
        shard_rows = 32
        for start in range(0, len(rows), shard_rows):
            batch = rows[start:start + shard_rows]
            key = hashlib.sha256(f"{checkpoint}:{bool(media)}:{index_digest(batch)}".encode()).hexdigest()
            shard = text_cache / f"{pool}-{key}.npz"
            if not shard.exists():
                t = model.encode_document([document_text(row) for row in batch], normalize_embeddings=True,
                                          batch_size=batch_size, show_progress_bar=False)
                c, o = encode_payloads(model, batch, batch_size)
                save_index(shard, text=t, chunks=c, chunk_owners=o)
            with np.load(shard, allow_pickle=False) as saved:
                texts.append(saved["text"])
                payloads.append(saved["chunks"])
                payload_owners.append(saved["chunk_owners"] + start)
            print(f"{pool} text records: {min(start + shard_rows, len(rows))}/{len(rows)}", flush=True)
        text = np.concatenate(texts)
        chunks = np.concatenate(payloads)
        chunk_owners = np.concatenate(payload_owners)
    path = index_path(pool)
    save_index(path, version=INDEX_VERSION, model=checkpoint, corpus=index_digest(rows), text=text,
               visual_coverage="text_only" if text_only else "all_local_media",
               chunks=chunks, chunk_owners=chunk_owners,
               visual=np.asarray(visual, dtype=np.float32).reshape(-1, DIM),
               owners=owners, asset_indices=asset_indices, starts=starts)
    print(f"{path}: {len(rows)} text records, {len(chunks)} payload chunks, "
          f"{len(visual)} visual windows", flush=True)


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("rebuild", "rebuild-components"))
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--visual-cache", type=Path, help="Reuse previously encoded assets during a rebuild")
    parser.add_argument("--text-cache", type=Path, help="Save resumable content-addressed text shards")
    parser.add_argument("--text-only", action="store_true", help="Index all text but explicitly omit local visual windows")
    args = parser.parse_args()
    build_index("components" if args.operation == "rebuild-components" else "showcases",
                args.batch_size, args.visual_cache, text_only=args.text_only, text_cache=args.text_cache)


if __name__ == "__main__":
    main()
