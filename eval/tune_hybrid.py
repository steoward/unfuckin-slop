#!/usr/bin/env python3
"""Tune the lexical/semantic hybrid weight on the dev split only.

Drives the *actual* deployed search() pipeline at each weight (not an offline
approximation), so the selected weight reproduces exactly in production.
hybrid = (1-w)*minmax(lexical) + w*minmax(semantic), computed inside search().
"""
import argparse
import importlib.util
import json
import os

import numpy as np

import evaluate as ev

REPO = ev.REPO


def load_sds():
    spec = importlib.util.spec_from_file_location(
        "sds", os.path.join(REPO, "search_design_showcases.py"))
    sds = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sds)
    # Design specs do not affect ranking; stub them out for speed.
    sds.derive_ui_design_spec = lambda *a, **k: {}
    return sds


def score_matrix(sds, meta, queries):
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    meta = ev.load_meta()
    queries = ev.load_bench()
    sds = load_sds()
    if sds._load_semantic()[0] is None:
        raise RuntimeError("semantic encoder unavailable; cannot tune hybrid")

    rows = []
    for w in [round(x * 0.1, 1) for x in range(11)]:
        sds.SEMANTIC_WEIGHT = w
        scores = score_matrix(sds, meta, queries)
        rows.append({"w": w,
                     "dev": ev.aggregate(scores, queries, "dev"),
                     "test": ev.aggregate(scores, queries, "test")})
        print(f"w={w:.1f}  dev={rows[-1]['dev']}  test={rows[-1]['test']}", flush=True)

    best = max(rows, key=lambda r: (r["dev"]["MRR@10"], r["dev"]["nDCG@5"]))
    print(f"\nbest by dev MRR: w={best['w']}  dev={best['dev']}  test={best['test']}")
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump({"grid": rows, "best": best}, f, indent=2)


if __name__ == "__main__":
    main()