#!/usr/bin/env python3
"""Fine-tune all-MiniLM-L6-v2 for design-showcase retrieval on CPU.

Two recipes compared:
  control  - reproduces the repo notebook: anchor = "title - description [Category]",
             positive = "UI Pattern: ... Video Asset: URL ... Behavior: ..." (3 epochs).
             Note the notebook indexes "title: description" but trains on a different
             positive text - a train/index mismatch we keep here for fidelity.
  query    - our improved recipe: short natural query-style anchors -> positive is
             exactly the indexed text "title: description". Three phases (1 epoch each):
             A: title-derived query, B: description-derived query, C: mixed.
             One anchor per item per batch => no false in-batch negatives.

Dev-split metrics are computed after every phase; the best dev checkpoint wins.
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

OUT_ROOT = "D:/unfslop-ft/models"
BASE_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

STOP = {"a", "an", "the", "and", "or", "for", "with", "of", "in", "on", "to", "is",
        "featuring", "showcasing", "showing", "displaying", "demonstrating", "made",
        "by", "curated", "from", "internet", "this", "that", "into", "over"}


def clean_title(title):
    t = re.sub(r":\s*(App Design|Website Design.*|Ad Design|Launch Film.*|App Design.*|Utilities App Design|Feature Announcement.*|Product Demo.*|AI App Design.*|Finance App Design.*|Design Tools.*|Developer Tools.*|SaaS Website.*|AI Website.*|Crypto and Web3.*|Finance and Fintech.*|Portfolio Website.*|Agency and Studio.*|Media and Editorial.*|Carousel and Gallery.*|Creative Experiments.*|Widget UI.*|Productivity App.*|Health and Wellness.*|Food and Drink.*|Events and Conferences.*|Business and SaaS.*|Social and Community.*|Ecommerce Website.*|Design Tools App.*)$", "", title)
    t = re.sub(r"\s*(Showcase|Motion Showcase|UI Concept|Concept|Inspiration)$", "", t)
    return t.strip().lower()


def desc_query(desc):
    d = re.sub(r"(Made by [^.]+\.|Curated from the internet\.)", "", desc).strip()
    d = re.sub(r"^(A|An|The)\s+", "", d)
    d = re.sub(r"^(clean|sleek|minimalist|modern|interactive|animated|dynamic|dark[- ]mode|light[- ]mode)[, ]+", "", d, flags=re.I)
    words = d.split()
    return " ".join(words[:14]).lower().rstrip(".,;:")


def title_query(title):
    return clean_title(title)


def mixed_query(rec, rng):
    if rng.random() < 0.5:
        return title_query(rec["title"])
    return desc_query(rec["description"])


def notebook_pair(rec):
    anchor = f"{rec['title']} - {rec['description']}"
    if rec.get("category"):
        anchor += f" [Category: {rec['category']}]"
    pos = f"UI Pattern: {rec['title']}. "
    if rec.get("video_url"):
        pos += f"Video Asset: {rec['video_url']}. "
    pos += f"Behavior: {rec['description']}. "
    if rec.get("is_liquid_glass"):
        pos += "Visual Engine: Liquid Glass Refraction & Chromatic Aberration. "
    if rec.get("is_3d"):
        pos += "Visual Engine: 3D Spatial Canvas & Three.js Particle Orbit. "
    return anchor, pos


def index_text(rec):
    return f"{rec['title']}: {rec['description']}"


def dev_metrics(model, meta, queries):
    texts = [index_text(m) for m in meta]
    doc_emb = model.encode(texts, normalize_embeddings=True, show_progress_bar=False,
                           batch_size=64, convert_to_numpy=True)
    dev_q = [q for q in queries if q["split"] == "dev"]
    scores = ev.system_semantic(meta, dev_q, model, doc_emb)
    return ev.aggregate(scores, dev_q)


def train_recipe(recipe, meta, queries, epochs, lr, batch_size):
    from sentence_transformers import (SentenceTransformer, SentenceTransformerTrainer,
                                       SentenceTransformerTrainingArguments)
    from sentence_transformers.losses import MultipleNegativesRankingLoss
    from datasets import Dataset

    rng = random.Random(42)
    model = SentenceTransformer(BASE_MODEL)
    model.max_seq_length = 128
    loss = MultipleNegativesRankingLoss(model)
    log = []

    if recipe == "control":
        pairs = [notebook_pair(m) for m in meta]
        phases = [("control", pairs)] * epochs
    else:
        phases = [
            ("A_title", [(title_query(m["title"]), index_text(m)) for m in meta]),
            ("B_desc", [(desc_query(m["description"]), index_text(m)) for m in meta]),
            ("C_mixed", [(mixed_query(m, rng), index_text(m)) for m in meta]),
        ]

    for i, (phase_name, pairs) in enumerate(phases, 1):
        ds = Dataset.from_dict({"anchor": [p[0] for p in pairs],
                                "positive": [p[1] for p in pairs]})
        out_dir = os.path.join(OUT_ROOT, f"{recipe}_phase{i}")
        args = SentenceTransformerTrainingArguments(
            output_dir=out_dir,
            num_train_epochs=1,
            per_device_train_batch_size=batch_size,
            learning_rate=lr,
            warmup_ratio=0.1,
            fp16=False,
            use_cpu=True,
            logging_steps=10,
            save_strategy="no",
            report_to="none",
        )
        trainer = SentenceTransformerTrainer(model=model, train_dataset=ds, loss=loss, args=args)
        print(f"\n--- recipe={recipe} phase {i}/{len(phases)} ({phase_name}), {len(ds)} pairs ---", flush=True)
        trainer.train()
        model.save_pretrained(out_dir)
        m = dev_metrics(model, meta, queries)
        log.append({"phase": phase_name, "dir": out_dir, "dev": m})
        print(f"dev after {phase_name}: {m}", flush=True)

    return log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--recipe", choices=["query", "control"], required=True)
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--batch-size", type=int, default=32)
    args = ap.parse_args()

    meta = ev.load_meta()
    queries = ev.load_bench()
    os.makedirs(OUT_ROOT, exist_ok=True)
    log = train_recipe(args.recipe, meta, queries, args.epochs, args.lr, args.batch_size)
    log_path = os.path.join(OUT_ROOT, f"{args.recipe}_log.json")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)
    best = max(log, key=lambda r: r["dev"]["MRR@10"])
    print(f"\nBEST dev checkpoint: {best['dir']}  dev={best['dev']}")
    print(f"log: {log_path}")


if __name__ == "__main__":
    main()