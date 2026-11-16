#!/usr/bin/env python3
"""Retrieval benchmark for the design showcase index.

Systems compared:
  current      - the deployed search() pipeline (TF-IDF + keyword boosts), called as-is
  stored       - repo design_embeddings.npy queried with base MiniLM (weights of the old
                 fine-tune are not in the repo; base MiniLM is the compatible query encoder)
  base         - base all-MiniLM-L6-v2, docs = "title: description"
  <model_path> - any fine-tuned SentenceTransformer checkpoint

Metrics: P@1, Recall@5, MRR@10, nDCG@5. Reported per split (dev/test) and overall.
"""
import argparse
import importlib.util
import json
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META_PATH = os.path.join(REPO, "design_showcases", "showcases_meta.json")
BENCH_PATH = os.path.join(REPO, "eval", "benchmark.json")
STORED_EMB = os.path.join(REPO, "design_showcases", "design_embeddings.npy")
CACHE_DIR = os.environ.get("UNFSLOP_EVAL_CACHE", "D:/unfslop-ft/cache")
BASE_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def load_meta():
    with open(META_PATH, encoding="utf-8") as f:
        return json.load(f)


def doc_texts(meta):
    return [f"{m['title']}: {m['description']}" for m in meta]


def load_bench():
    with open(BENCH_PATH, encoding="utf-8") as f:
        return json.load(f)["queries"]


def encode_cached(model, texts, cache_key):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, cache_key + ".npy")
    if os.path.exists(path):
        return np.load(path)
    emb = model.encode(texts, normalize_embeddings=True, show_progress_bar=False,
                       batch_size=64, convert_to_numpy=True)
    np.save(path, emb)
    return emb


def rank_to_scores(ranked_ids, n):
    """ranked_ids: list of doc indices best-first -> dense score array (higher=better)."""
    scores = np.zeros(n)
    for rank, idx in enumerate(ranked_ids):
        scores[idx] = len(ranked_ids) - rank
    return scores


def system_current(meta, queries, disable_semantic=False):
    spec = importlib.util.spec_from_file_location(
        "sds", os.path.join(REPO, "search_design_showcases.py"))
    sds = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sds)
    if disable_semantic:
        sds._sem_state.update({"loaded": True, "enc": None, "emb": None})
    id_to_idx = {m["id"]: i for i, m in enumerate(meta)}
    out = []
    for q in queries:
        results = sds.search(query=q["query"], limit=len(meta))
        scores = np.zeros(len(meta))
        for r in results:
            if r["id"] in id_to_idx:
                scores[id_to_idx[r["id"]]] = float(r.get("relevance_score", 0.0))
        out.append(scores)
    return np.array(out)


def system_onnx(meta, queries):
    """Pure semantic scores from the deployed int8 ONNX encoder + index."""
    sys.path.insert(0, REPO)
    import semantic_index
    enc = semantic_index.load_encoder()
    if enc is None:
        raise RuntimeError("ONNX encoder unavailable")
    doc_emb = np.load(STORED_EMB)
    qemb = enc.encode([q["query"] for q in queries])
    return qemb @ doc_emb.T


def system_semantic(meta, queries, model, doc_emb, query_prompt=None):
    qtexts = [q["query"] for q in queries]
    if query_prompt:
        qemb = model.encode(qtexts, prompt=query_prompt, normalize_embeddings=True,
                            show_progress_bar=False, convert_to_numpy=True)
    else:
        qemb = model.encode(qtexts, normalize_embeddings=True, show_progress_bar=False,
                            batch_size=64, convert_to_numpy=True)
    return qemb @ doc_emb.T


def metrics(scores, relevant, ks=(1, 5, 10)):
    order = np.argsort(-scores)
    rel = set(relevant)
    p1 = 1.0 if order[0] in rel else 0.0
    recall5 = len(rel & set(order[:5].tolist())) / len(rel)
    mrr = 0.0
    for r, idx in enumerate(order[:10], 1):
        if idx in rel:
            mrr = 1.0 / r
            break
    dcg = sum(1.0 / np.log2(r + 1) for r, idx in enumerate(order[:5], 1) if idx in rel)
    idcg = sum(1.0 / np.log2(r + 1) for r in range(1, min(len(rel), 5) + 1))
    ndcg5 = dcg / idcg if idcg else 0.0
    return {"P@1": p1, "R@5": recall5, "MRR@10": mrr, "nDCG@5": ndcg5}


def aggregate(score_rows, queries, split=None):
    rows = []
    for scores, q in zip(score_rows, queries):
        if split and q["split"] != split:
            continue
        rows.append(metrics(scores, q["relevant"]))
    if not rows:
        return {}
    return {k: round(float(np.mean([r[k] for r in rows])), 4) for k in rows[0]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--systems", nargs="+", required=True,
                    help="current | stored | base | path/to/checkpoint")
    ap.add_argument("--out", default=None, help="write JSON results here")
    ap.add_argument("--save-scores", default=None,
                    help="directory to save per-system score matrices (for hybrid tuning)")
    args = ap.parse_args()

    meta = load_meta()
    queries = load_bench()
    texts = doc_texts(meta)
    results = {}
    score_dump = {}

    from sentence_transformers import SentenceTransformer
    base_model = None

    for name in args.systems:
        if name == "current":
            scores = system_current(meta, queries)
        elif name == "lexical":
            scores = system_current(meta, queries, disable_semantic=True)
        elif name == "onnx":
            scores = system_onnx(meta, queries)
        elif name == "stored":
            if base_model is None:
                base_model = SentenceTransformer(BASE_MODEL)
            doc_emb = np.load(STORED_EMB)
            scores = system_semantic(meta, queries, base_model, doc_emb)
        elif name == "base":
            if base_model is None:
                base_model = SentenceTransformer(BASE_MODEL)
            doc_emb = encode_cached(base_model, texts, "base_minilm_docs")
            scores = system_semantic(meta, queries, base_model, doc_emb)
        else:
            model = SentenceTransformer(name)
            key = "ft_" + os.path.basename(os.path.normpath(name)).replace(".", "_")
            doc_emb = encode_cached(model, texts, key + "_docs")
            scores = system_semantic(meta, queries, model, doc_emb)
        results[name] = {
            "dev": aggregate(scores, queries, "dev"),
            "test": aggregate(scores, queries, "test"),
            "all": aggregate(scores, queries),
        }
        score_dump[name] = scores
        print(f"\n=== {name} ===")
        for split in ("dev", "test", "all"):
            print(f"  {split:5s} {results[name][split]}")

    if args.save_scores:
        os.makedirs(args.save_scores, exist_ok=True)
        for name, scores in score_dump.items():
            safe = name.replace("/", "_").replace("\\", "_").replace(":", "")
            np.save(os.path.join(args.save_scores, safe + ".npy"), scores)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()