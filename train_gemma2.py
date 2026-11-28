"""Fit a domain LoRA for EmbeddingGemma 2 using text and local visual assets."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import random
from tempfile import TemporaryDirectory

import torch
import torch.nn.functional as F
from peft import LoraConfig

from semantic_index import (
    VISUAL_CACHE_VERSION, VISUAL_WINDOW_SECONDS, canonical_rows, document_text, load_encoder,
    media_windows, model_key, row_digest,
)


def reference_query(row):
    title = row["title"]
    category = row.get("category")
    tags = ", ".join(row.get("tags") or [])
    return " | ".join(filter(None, [title, category, tags]))


def training_examples(rows, tokenizer, use_media):
    for row in rows:
        query = reference_query(row)
        yield "text", row["id"], query, document_text(row), row["id"]
        body = row.get("full_prompt")
        if body:
            tokens = tokenizer.encode(body, add_special_tokens=False, truncation=False, verbose=False)
            for offset in range(0, len(tokens), 384):
                chunk = tokenizer.decode(tokens[offset:offset + 384], skip_special_tokens=True)
                yield "text", row["id"], query, chunk, row["id"]
        if use_media:
            for asset in row.get("media", []):
                for start, media in media_windows(asset):
                    unit = f"{row['id']}:{asset['sha256']}"
                    yield asset["kind"], row["id"], query, media, (unit, f"{unit}:{start}")


def encode(model, values, prompt=None):
    features = model.preprocess(values, prompt=prompt)
    features = {name: value.to(model.device) if isinstance(value, torch.Tensor) else value
                for name, value in features.items()}
    return F.normalize(model(features)["sentence_embedding"].float(), dim=-1)


def batches(rows, tokenizer, use_media, batch_size):
    pending = defaultdict(list)
    for kind, record_id, query, value, unit in training_examples(rows, tokenizer, use_media):
        batch = pending[kind]
        batch.append((record_id, query, value, unit))
        if len(batch) == batch_size:
            yield kind, batch[:]
            batch.clear()
    for kind, batch in pending.items():
        if batch:
            yield kind, batch


def train_step(model, batch, kind, negative):
    ids, queries, values, _ = zip(*batch)
    anchor = encode(model, list(queries), model.prompts["query"])
    positive = encode(model, list(values), model.prompts["document"] if kind == "text" else None)
    logits = 20 * (anchor @ positive.T)
    for i, row_id in enumerate(ids):
        for j, other_id in enumerate(ids):
            if i != j and row_id == other_id:
                logits[i, j] = -torch.inf
    # Match the text and visual modalities to the same text-query space.
    # A cross-record text decoy supplies a negative even for a single visual pair.
    if negative is not None:
        decoy = encode(model, [negative], model.prompts["document"])
        logits = torch.cat((logits, 20 * (anchor @ decoy.T)), dim=1)
    return F.cross_entropy(logits, torch.arange(len(batch), device=model.device))


def coverage_units(kind, batch, coverage):
    for _, _, _, unit in batch:
        if kind == "text":
            coverage[kind].add(unit)
        else:
            asset, window = unit
            coverage[kind].add(asset)
            coverage[f"{kind}_windows"].add(window)


def checkpoint(model, optimizer, output, step, counts, covered, signature, epoch, next_batch, *, final=False):
    folder = output / f"step-{step:08d}"
    if final and folder.exists():
        folder = folder.with_name(f"{folder.name}-final")
    if folder.exists():
        raise FileExistsError(f"Checkpoint already exists: {folder}")
    output.mkdir(parents=True, exist_ok=True)
    report = {"step": step, "examples": dict(counts), "training_signature": signature,
              "epoch": epoch, "next_batch": next_batch,
              "covered": {kind: sorted(units) for kind, units in covered.items()}}
    with TemporaryDirectory(prefix=".checkpoint-", dir=output) as temporary:
        staged = Path(temporary) / "checkpoint"
        model[0].model.save_pretrained(staged)
        state = {"optimizer": optimizer.state_dict(), "cpu_rng": torch.get_rng_state()}
        if model.device.type == "cuda":
            state["cuda_rng"] = torch.cuda.get_rng_state(model.device)
        torch.save(state, staged / "optimizer.pt")
        (staged / "coverage.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        staged.rename(folder)
    return folder


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--save-every", type=int, default=250)
    parser.add_argument("--resume", type=Path)
    parser.add_argument("--limit", type=int, help="Bound the smoke-test corpus")
    parser.add_argument("--steps", type=int, help="Bound the smoke-test steps")
    parser.add_argument("--text-only", action="store_true")
    args = parser.parse_args()
    if min(args.batch_size, args.epochs, args.save_every) < 1:
        parser.error("batch size, epochs and checkpoint interval must be positive")
    if any(value is not None and value < 1 for value in (args.limit, args.steps)):
        parser.error("limit and steps must be positive")
    rows = canonical_rows("showcases") + canonical_rows("components")
    if args.limit:
        rows = rows[:args.limit]
    if len(rows) < 2:
        parser.error("training requires at least two source records")
    use_media = not args.text_only and any(row.get("media") for row in rows)
    fingerprint = hashlib.sha256(
        f"coverage-v2:{model_key(adapter=False)}:{row_digest(rows)}:"
        f"{args.batch_size}:{use_media}:{VISUAL_CACHE_VERSION}:{VISUAL_WINDOW_SECONDS}".encode()
    )
    for row in rows:
        fingerprint.update(hashlib.sha256((row.get("full_prompt") or "").encode()).digest())
    signature = fingerprint.hexdigest()
    step, start_epoch, resume_batch = 0, 0, 0
    counts = Counter()
    covered = defaultdict(set)
    expected = defaultdict(set)
    for row in rows:
        expected["text"].add(row["id"])
        if use_media:
            for asset in row.get("media", []):
                expected[asset["kind"]].add(f"{row['id']}:{asset['sha256']}")
    if args.resume:
        previous = json.loads((args.resume / "coverage.json").read_text(encoding="utf-8"))
        if previous["training_signature"] != signature:
            parser.error("checkpoint format, base model, corpus, batch size or modality changed")
        step, start_epoch, resume_batch = previous["step"], previous["epoch"], previous["next_batch"]
        if start_epoch >= args.epochs:
            parser.error("checkpoint already reached the requested epoch count")
        if args.steps is not None and args.steps <= step:
            parser.error("step limit must be greater than the resumed step")
        counts.update(previous["examples"])
        covered.update({kind: set(units) for kind, units in previous["covered"].items()})
    model = load_encoder(vision=use_media, adapter=False)
    torch.manual_seed(124)
    if args.resume:
        model.load_adapter(str(args.resume), is_trainable=True)
    else:
        targets = [name for name, module in model[0].model.named_modules()
                   if name.startswith("language_model.") and name.rsplit(".", 1)[-1] in ("q_proj", "v_proj")
                   and isinstance(module, torch.nn.Linear)]
        if not targets:
            raise RuntimeError("No compatible EmbeddingGemma 2 language attention layers found")
        model.add_adapter(LoraConfig(r=8, lora_alpha=16, target_modules=targets,
                                    lora_dropout=0.0, bias="none"))
    model.train()
    trainable = [param for param in model.parameters() if param.requires_grad]
    print(f"model_device={model.device} trainable_parameters={sum(p.numel() for p in trainable)} records={len(rows)} media={use_media}", flush=True)
    optimizer = torch.optim.AdamW(trainable, lr=3e-5)
    if args.resume:
        state = torch.load(args.resume / "optimizer.pt", weights_only=True, map_location="cpu")
        optimizer.load_state_dict(state["optimizer"])
        torch.set_rng_state(state["cpu_rng"])
        if model.device.type == "cuda" and "cuda_rng" in state:
            torch.cuda.set_rng_state(state["cuda_rng"], model.device)
    tokenizer = model.tokenizer
    for epoch in range(start_epoch, args.epochs):
        ordered = list(rows)
        rng = random.Random(124 + epoch)
        rng.shuffle(ordered)
        decoys = [(row["id"], document_text(row)) for row in ordered]
        for ordinal, (kind, batch) in enumerate(batches(ordered, tokenizer, use_media, args.batch_size)):
            coverage_units(kind, batch, expected)
            if epoch == start_epoch and ordinal < resume_batch:
                continue
            positives = {item[0] for item in batch}
            # Cycle through decoys deterministically across restarts.
            negative = next((text for offset in range(len(decoys))
                             for row_id, text in [decoys[(ordinal + offset) % len(decoys)]]
                             if row_id not in positives), None)
            optimizer.zero_grad(set_to_none=True)
            loss = train_step(model, batch, kind, negative)
            if not torch.isfinite(loss):
                raise RuntimeError(f"Non-finite training loss at step {step + 1}")
            loss.backward()
            torch.nn.utils.clip_grad_norm_(trainable, 1.0)
            optimizer.step()
            counts.update({kind: len(batch)})
            coverage_units(kind, batch, covered)
            step += 1
            if step % 25 == 0 or step == 1:
                print(f"step={step} {kind} loss={loss.item():.5f} coverage={dict(counts)}", flush=True)
            stopping = args.steps is not None and step >= args.steps
            if stopping or step % args.save_every == 0:
                checkpoint(model, optimizer, args.output, step, counts, covered, signature, epoch, ordinal + 1)
            if stopping:
                return
    missing = {kind: len(units - covered[kind]) for kind, units in expected.items()
               if units - covered[kind]}
    if missing:
        raise RuntimeError(f"Training finished with missing corpus entries: {missing}")
    final = checkpoint(model, optimizer, args.output, step, counts, covered, signature, args.epochs, 0,
                       final=True)
    print(f"Training complete: {final}; examples={dict(counts)}", flush=True)


if __name__ == "__main__":
    main()
