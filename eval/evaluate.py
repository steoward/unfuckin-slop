#!/usr/bin/env python3
"""Evaluate the search modes against the showcase benchmark."""
import argparse
import json
from pathlib import Path
import sys
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import search_design_showcases as catalog
from semantic_index import query_vectors, open_index


def metrics(order, relevant):
    relevant = set(relevant)
    recall = len(relevant.intersection(order[:5])) / len(relevant)
    reciprocal_rank = next((1 / rank for rank, idx in enumerate(order[:10], 1)
                            if idx in relevant), 0.0)
    dcg = sum(1 / np.log2(rank + 1) for rank, idx in enumerate(order[:5], 1)
              if idx in relevant)
    ideal_dcg = sum(1 / np.log2(rank + 1) for rank in range(1, min(len(relevant), 5) + 1))
    return {"P@1": float(bool(len(order) and order[0] in relevant)),
            "R@5": recall, "MRR@10": reciprocal_rank, "nDCG@5": dcg / ideal_dcg}


def search_orders(meta, queries):
    indices = {row["id"]: i for i, row in enumerate(meta)}
    return [[indices[row["id"]] for row in catalog.search(case["query"], limit=10, records=meta)]
            for case in queries]


def evaluate(system, meta, queries):
    if system == "lexical":
        with patch.object(catalog, "_load_semantic", return_value=(None, None)):
            orders = search_orders(meta, queries)
    elif system == "gemma2":
        index = open_index("showcases")
        if index is None:
            raise RuntimeError("Build the EmbeddingGemma 2 showcase index first")
        indices = list(range(len(meta)))
        scores = np.stack([index.rank_text(indices, vector)
                           for vector in query_vectors([case["query"] for case in queries])])
        orders = np.argsort(-scores, axis=1, kind="stable")
    else:
        if catalog._load_semantic()[1] is None:
            raise RuntimeError("Build the EmbeddingGemma 2 showcase index first")
        orders = search_orders(meta, queries)

    rows = [metrics(order, case["relevant"]) for order, case in zip(orders, queries)]
    results = {}
    for split in ("dev", "test", "all"):
        group = [row for case, row in zip(queries, rows) if split == "all" or case["split"] == split]
        results[split] = {key: round(float(np.mean([row[key] for row in group])), 4)
                          for key in group[0]}
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--systems", nargs="+", choices=("current", "lexical", "gemma2"),
                        default=("current", "lexical", "gemma2"))
    parser.add_argument("--out", type=Path, help="Write results to a JSON file")
    args = parser.parse_args()
    queries = json.loads((ROOT / "eval/benchmark.json").read_text(encoding="utf-8"))["queries"]
    meta = catalog.load_data()
    row_indices = {row["id"]: index for index, row in enumerate(meta)}
    for case in queries:
        missing = [record_id for record_id in case["relevant"] if record_id not in row_indices]
        if missing:
            parser.error(f"benchmark reference IDs missing: {', '.join(missing)}")
        case["relevant"] = [row_indices[record_id] for record_id in case["relevant"]]
    results = {name: evaluate(name, meta, queries) for name in args.systems}
    output = json.dumps(results, indent=2) + "\n"
    if args.out:
        args.out.write_text(output, encoding="utf-8")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
