#!/usr/bin/env python3
"""Semantic vector index for the design showcase library.

Encodes text with the bundled fine-tuned MiniLM ONNX encoder (uint8 per-channel, ~22 MB)
using only onnxruntime + tokenizers - no torch needed at search time.

Usage:
    python semantic_index.py rebuild              # regenerate design_embeddings.npy from meta
    python semantic_index.py rebuild-components   # regenerate component_embeddings.npy from components_meta
    python semantic_index.py encode "query text"  # debug: print a query vector norm

If onnxruntime/tokenizers or the encoder files are missing, `load_encoder()`
returns None and callers fall back to lexical search.
"""
import json
import os

import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHOWCASES_DIR = os.path.join(BASE_DIR, "design_showcases")
ENC_DIR = os.path.join(SHOWCASES_DIR, "encoder")
META_PATH = os.path.join(SHOWCASES_DIR, "showcases_meta.json")
EMBS_PATH = os.path.join(SHOWCASES_DIR, "design_embeddings.npy")
COMPONENTS_META_PATH = os.path.join(SHOWCASES_DIR, "components_meta.json")
COMPONENTS_EMBS_PATH = os.path.join(SHOWCASES_DIR, "component_embeddings.npy")


class OnnxEncoder:
    def __init__(self, enc_dir=ENC_DIR):
        import onnxruntime as ort
        from tokenizers import Tokenizer

        with open(os.path.join(enc_dir, "encoder_config.json"), encoding="utf-8") as f:
            self.cfg = json.load(f)
        self.sess = ort.InferenceSession(
            os.path.join(enc_dir, "model.onnx"), providers=["CPUExecutionProvider"])
        self.tok = Tokenizer.from_file(os.path.join(enc_dir, "tokenizer.json"))
        self.tok.enable_truncation(max_length=self.cfg.get("max_seq_length", 128))
        self.tok.enable_padding(pad_id=0, pad_token="[PAD]")

    def encode(self, texts, batch_size=64):
        if isinstance(texts, str):
            texts = [texts]
        out = []
        for i in range(0, len(texts), batch_size):
            enc = self.tok.encode_batch(texts[i:i + batch_size])
            feed = {
                "input_ids": np.array([e.ids for e in enc], dtype=np.int64),
                "attention_mask": np.array([e.attention_mask for e in enc], dtype=np.int64),
                "token_type_ids": np.array([e.type_ids for e in enc], dtype=np.int64),
            }
            out.append(self.sess.run(["embedding"], feed)[0])
        return np.vstack(out).astype(np.float32)


def load_encoder():
    try:
        return OnnxEncoder()
    except Exception:
        return None


def index_text(item):
    return f"{item['title']}: {item['description']}"


def build_index(verbose=True):
    enc = load_encoder()
    if enc is None:
        raise RuntimeError(
            "semantic encoder unavailable: pip install onnxruntime tokenizers "
            "and ensure design_showcases/encoder/ exists")
    with open(META_PATH, encoding="utf-8") as f:
        meta = json.load(f)
    texts = [index_text(m) for m in meta]
    emb = enc.encode(texts)
    np.save(EMBS_PATH, emb)
    if verbose:
        print(f"indexed {len(meta)} showcases -> {EMBS_PATH} shape={emb.shape}")
    return emb


def build_component_index(verbose=True):
    enc = load_encoder()
    if enc is None:
        raise RuntimeError(
            "semantic encoder unavailable: pip install onnxruntime tokenizers "
            "and ensure design_showcases/encoder/ exists")
    with open(COMPONENTS_META_PATH, encoding="utf-8") as f:
        meta = json.load(f)
    texts = [index_text(m) for m in meta]
    emb = enc.encode(texts)
    np.save(COMPONENTS_EMBS_PATH, emb)
    if verbose:
        print(f"indexed {len(meta)} components -> {COMPONENTS_EMBS_PATH} shape={emb.shape}")
    return emb


def main():
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "rebuild"
    if cmd == "rebuild":
        build_index()
    elif cmd == "rebuild-components":
        build_component_index()
    elif cmd == "encode":
        enc = load_encoder()
        if enc is None:
            print("encoder unavailable")
            sys.exit(1)
        v = enc.encode(" ".join(sys.argv[2:]))
        print(f"shape={v.shape} norm={np.linalg.norm(v[0]):.4f}")
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()