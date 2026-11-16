#!/usr/bin/env python3
"""Improved fine-tune recipe v2: description-grounded query anchors.

v1 showed that ~53% of title-derived anchors are brand-only (<=2 words) and
inject noise into MNRL. v2 anchors every item on its description (always rich
in design semantics), uses descriptive titles only when they carry >=3 content
words, trims dangling function words, and uses a gentler lr.
"""
import argparse
import json
import os
import random
import re
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "eval"))
import evaluate as ev  # noqa: E402
from train import clean_title, index_text, dev_metrics, OUT_ROOT, BASE_MODEL  # noqa: E402

TRAIL = {"a", "an", "the", "and", "or", "for", "with", "of", "in", "on", "to",
         "is", "into", "over", "from", "by", "at", "as", "that", "this", "its",
         "featuring", "showcasing", "showing", "displaying", "demonstrating",
         "followed", "while", "during", "across", "around", "between"}


def desc_anchor(desc, max_words=14):
    d = re.sub(r"(Made by [^.]+\.|Curated from the internet\.)", "", desc).strip()
    d = re.sub(r"^(A|An|The)\s+", "", d)
    d = re.sub(r"^(clean|sleek|minimalist|modern|interactive|animated|dynamic|dark[- ]mode|light[- ]mode)[, ]+", "", d, flags=re.I)
    words = d.split()[:max_words]
    while words and words[-1].lower().strip(".,;:") in TRAIL:
        words.pop()
    return " ".join(words).lower().rstrip(".,;:")


def title_anchor(title):
    t = clean_title(title)
    words = [w for w in re.split(r"[\s:,.]+", t) if w]
    if len(words) < 3:
        return None
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lr", type=float, default=1e-5)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--tag", default="queryv2")
    args = ap.parse_args()

    from sentence_transformers import (SentenceTransformer, SentenceTransformerTrainer,
                                       SentenceTransformerTrainingArguments)
    from sentence_transformers.losses import MultipleNegativesRankingLoss
    from datasets import Dataset

    meta = ev.load_meta()
    queries = ev.load_bench()
    rng = random.Random(7)

    phases = [
        ("A_desc14", [(desc_anchor(m["description"], 14), index_text(m)) for m in meta]),
        ("B_desc20", [(desc_anchor(m["description"], 20), index_text(m)) for m in meta]),
        ("C_title_or_desc", [((title_anchor(m["title"]) or desc_anchor(m["description"], 14)), index_text(m)) for m in meta]),
    ]

    model = SentenceTransformer(BASE_MODEL)
    model.max_seq_length = 128
    loss = MultipleNegativesRankingLoss(model)
    log = []
    for i, (name, pairs) in enumerate(phases, 1):
        ds = Dataset.from_dict({"anchor": [p[0] for p in pairs], "positive": [p[1] for p in pairs]})
        out_dir = os.path.join(OUT_ROOT, f"{args.tag}_phase{i}")
        targs = SentenceTransformerTrainingArguments(
            output_dir=out_dir, num_train_epochs=1,
            per_device_train_batch_size=args.batch_size, learning_rate=args.lr,
            warmup_steps=0.1, fp16=False, use_cpu=True, logging_steps=10,
            save_strategy="no", report_to="none")
        trainer = SentenceTransformerTrainer(model=model, train_dataset=ds, loss=loss, args=targs)
        print(f"\n--- {args.tag} phase {i}/3 ({name}) ---", flush=True)
        trainer.train()
        model.save_pretrained(out_dir)
        m = dev_metrics(model, meta, queries)
        log.append({"phase": name, "dir": out_dir, "dev": m})
        print(f"dev after {name}: {m}", flush=True)

    with open(os.path.join(OUT_ROOT, f"{args.tag}_log.json"), "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)
    best = max(log, key=lambda r: (r["dev"]["MRR@10"], r["dev"]["nDCG@5"]))
    print(f"\nBEST dev checkpoint: {best['dir']}  dev={best['dev']}")


if __name__ == "__main__":
    main()