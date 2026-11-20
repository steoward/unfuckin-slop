#!/usr/bin/env python3
"""Export a fine-tuned SentenceTransformer checkpoint to a bundled ONNX encoder.

Writes design_showcases/encoder/{model.onnx,tokenizer.json,encoder_config.json}.
The per-channel uint8 dynamic-quantized MiniLM encoder is ~23 MB and runs on
onnxruntime + tokenizers alone (no torch at search time). Per-channel uint8
keeps ~0.99 cosine parity with the float model (vs ~0.96 for per-tensor int8),
recovering most of the quantization retrieval loss at the same size. Verifies
numerical parity against the torch model before writing.
"""
import argparse
import json
import os
import shutil

import numpy as np
import torch

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENC_DIR = os.path.join(REPO, "design_showcases", "encoder")


class EncoderWrapper(torch.nn.Module):
    def __init__(self, auto_model):
        super().__init__()
        self.model = auto_model

    def forward(self, input_ids, attention_mask, token_type_ids):
        out = self.model(input_ids=input_ids, attention_mask=attention_mask,
                         token_type_ids=token_type_ids).last_hidden_state
        mask = attention_mask.unsqueeze(-1).float()
        mean = (out * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1e-9)
        return torch.nn.functional.normalize(mean, p=2, dim=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--max-seq", type=int, default=128)
    args = ap.parse_args()

    from sentence_transformers import SentenceTransformer
    st = SentenceTransformer(args.checkpoint)
    st.max_seq_length = args.max_seq
    auto_model = st[0].auto_model
    auto_model.eval()
    wrapper = EncoderWrapper(auto_model).eval()

    sample = ["liquid glass refraction hero", "dark analytics dashboard with KPI cards",
              "3d particle orbit webgl hero", "fashion lookbook clothing rail"]
    feat = st.tokenize(sample)
    feat = {k: v for k, v in feat.items() if k in ("input_ids", "attention_mask", "token_type_ids")}
    with torch.no_grad():
        ref = wrapper(**feat).numpy()

    os.makedirs(ENC_DIR, exist_ok=True)
    fp32_path = os.path.join(ENC_DIR, "model_fp32.onnx")
    torch.onnx.export(
        wrapper, (feat["input_ids"], feat["attention_mask"], feat["token_type_ids"]),
        fp32_path, input_names=["input_ids", "attention_mask", "token_type_ids"],
        output_names=["embedding"],
        dynamic_axes={k: {0: "batch", 1: "seq"} for k in
                      ("input_ids", "attention_mask", "token_type_ids", "embedding")},
        opset_version=17, do_constant_folding=True, dynamo=False,
    )

    from onnxruntime.quantization import quantize_dynamic, QuantType
    quant_path = os.path.join(ENC_DIR, "model.onnx")
    quantize_dynamic(fp32_path, quant_path, weight_type=QuantType.QUInt8, per_channel=True)
    os.remove(fp32_path)

    import onnxruntime as ort
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(os.path.join(args.checkpoint, "tokenizer.json"))
    tok.enable_truncation(max_length=args.max_seq)
    tok.enable_padding(pad_id=0, pad_token="[PAD]")
    sess = ort.InferenceSession(quant_path, providers=["CPUExecutionProvider"])

    def onnx_encode(texts):
        enc = tok.encode_batch(texts)
        feed = {
            "input_ids": np.array([e.ids for e in enc], dtype=np.int64),
            "attention_mask": np.array([e.attention_mask for e in enc], dtype=np.int64),
            "token_type_ids": np.array([e.type_ids for e in enc], dtype=np.int64),
        }
        return sess.run(["embedding"], feed)[0]

    q = onnx_encode(sample)
    cos = (q * ref).sum(axis=1) / (np.linalg.norm(q, axis=1) * np.linalg.norm(ref, axis=1))
    print("torch vs onnx-uint8 cosine:", np.round(cos, 5))
    # Per-channel uint8 dynamic quantization drifts ~0.99 per vector (vs ~0.96 for
    # per-tensor int8); retrieval ranking is validated end-to-end on
    # eval/benchmark.json (see eval/evaluate.py system_current).
    assert cos.min() > 0.95, f"quantization drift too large: {cos}"

    st_ref = st.encode(sample, normalize_embeddings=True)
    cos2 = (q * st_ref).sum(axis=1)
    print("ST vs onnx-uint8 cosine:", np.round(cos2, 5))
    assert cos2.min() > 0.95

    tok.save(os.path.join(ENC_DIR, "tokenizer.json"))
    cfg = {"max_seq_length": args.max_seq, "dim": int(ref.shape[1]),
           "base_model": "sentence-transformers/all-MiniLM-L6-v2",
           "checkpoint": os.path.basename(os.path.normpath(args.checkpoint)),
           "pooling": "mean", "normalize": True, "quantization": "uint8_perchannel"}
    with open(os.path.join(ENC_DIR, "encoder_config.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    size = os.path.getsize(quant_path) / 1e6
    print(f"encoder written to {ENC_DIR} (model.onnx {size:.1f} MB)")


if __name__ == "__main__":
    main()