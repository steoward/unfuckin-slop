#!/usr/bin/env python3
"""Smoke tests for the semantic search layer (run after exporting the encoder).

    python eval/smoke_test.py

Checks: encoder loads and produces unit 384-d vectors; the index matches the meta
count; hybrid search returns sensible results; and the lexical fallback still works
when the semantic layer is unavailable.
"""
import os
import sys
from unittest.mock import patch

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import semantic_index  # noqa: E402
import search_design_showcases as sds  # noqa: E402


def main():
    enc = semantic_index.load_encoder()
    assert enc is not None, "encoder failed to load (pip install onnxruntime tokenizers)"
    v = enc.encode(["liquid glass refraction hero", "dark analytics dashboard"])
    assert v.shape == (2, 384), v.shape
    assert np.allclose(np.linalg.norm(v, axis=1), 1.0, atol=1e-3), "vectors not normalized"
    print("[ok] encoder produces unit 384-d vectors")

    emb = np.load(sds.EMBS_PATH)
    meta = sds.load_data()
    assert emb.shape == (len(meta), 384), (emb.shape, len(meta))
    assert np.allclose(np.linalg.norm(emb, axis=1), 1.0, atol=1e-2)
    print(f"[ok] index aligned with meta: {emb.shape}")

    res = sds.search("liquid glass refraction with chromatic aberration", limit=5)
    assert res, "hybrid search returned nothing"
    assert any(sds.is_liquid_glass_showcase(r) for r in res[:3]), "top results not liquid glass"
    print(f"[ok] hybrid search top hit: {res[0]['title']} (score {res[0]['relevance_score']})")

    res3d = sds.search("3d particle orbit webgl hero", limit=5, filter_3d=True)
    assert res3d and all(sds.is_3d_showcase(r) for r in res3d)
    print(f"[ok] --3d filter respected: {res3d[0]['title']}")

    # Force lexical fallback
    with patch.object(sds, "_load_semantic", return_value=(None, None)):
        res_fb = sds.search("liquid glass refraction", limit=5)
    assert res_fb, "lexical fallback returned nothing"
    print(f"[ok] lexical fallback works: {res_fb[0]['title']}")

    print("\nALL SMOKE TESTS PASSED")


if __name__ == "__main__":
    main()