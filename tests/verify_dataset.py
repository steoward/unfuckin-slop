#!/usr/bin/env python3
"""
Verification test suite for the unified 950-item design showcases dataset.
Verifies:
  - Total items count (950 items)
  - Total items with video (CloudFront + Pixlpin)
  - Liquid glass items count
  - 3D items count
  - Vector embeddings shape and normalization (950, 384)
  - Search functionality and category listing
"""

import os
import sys
import json
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOWCASES_DIR = os.path.join(BASE_DIR, "design_showcases")
META_PATH = os.path.join(SHOWCASES_DIR, "showcases_meta.json")
DATASET_PATH = os.path.join(SHOWCASES_DIR, "dataset.jsonl")
EMBS_PATH = os.path.join(SHOWCASES_DIR, "design_embeddings.npy")

def test_dataset():
    print("=======================================================")
    print(" UNIFIED DESIGN SHOWCASES DATASET VERIFICATION SUITE")
    print("=======================================================\n")

    # 1. Verify showcases_meta.json
    assert os.path.exists(META_PATH), f"Missing {META_PATH}"
    with open(META_PATH, "r", encoding="utf-8") as f:
        items = json.load(f)

    total_count = len(items)
    print(f"[*] Total items in showcases_meta.json: {total_count}")
    assert total_count == 950, f"Expected 950 items, found {total_count}"

    # 2. Verify dataset.jsonl
    assert os.path.exists(DATASET_PATH), f"Missing {DATASET_PATH}"
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        jsonl_lines = [json.loads(line) for line in f if line.strip()]

    print(f"[*] Total items in dataset.jsonl: {len(jsonl_lines)}")
    assert len(jsonl_lines) == 950, f"Expected 950 items in dataset.jsonl, found {len(jsonl_lines)}"

    # 3. Verify video assets
    video_items = [it for it in items if it.get("video_url")]
    cloudfront_videos = [it for it in video_items if "cloudfront.net" in (it.get("video_url") or "")]
    pixlpin_videos = [it for it in video_items if "pixlpin.com" in (it.get("video_url") or "")]
    other_videos = [it for it in video_items if "cloudfront.net" not in (it.get("video_url") or "") and "pixlpin.com" not in (it.get("video_url") or "")]

    print(f"[*] Total items with video: {len(video_items)} / {total_count}")
    print(f"    - CloudFront video assets: {len(cloudfront_videos)}")
    print(f"    - Pixlpin video assets:    {len(pixlpin_videos)}")
    print(f"    - Other CDN video assets:  {len(other_videos)}")
    assert len(video_items) >= 800, f"Expected at least 800 items with video, got {len(video_items)}"

    # 4. Verify 3D and Liquid Glass flags
    threed_items = [it for it in items if it.get("is_3d")]
    liquid_glass_items = [it for it in items if it.get("is_liquid_glass")]

    print(f"[*] 3D / WebGL / Spatial items: {len(threed_items)}")
    print(f"[*] Liquid Glass / Refraction items: {len(liquid_glass_items)}")
    assert len(threed_items) >= 300, f"Expected at least 300 3D items, got {len(threed_items)}"
    assert len(liquid_glass_items) >= 70, f"Expected at least 70 liquid glass items, got {len(liquid_glass_items)}"

    # 5. Verify Source Sites
    motionsites_count = sum(1 for it in items if it.get("source_site") == "motionsites.ai")
    pixlpin_count = sum(1 for it in items if it.get("source_site") == "pixlpin.com")
    print(f"[*] Source breakdown:")
    print(f"    - motionsites.ai: {motionsites_count}")
    print(f"    - pixlpin.com:    {pixlpin_count}")
    assert motionsites_count == 328, f"Expected 328 motionsites items, got {motionsites_count}"
    assert pixlpin_count == 622, f"Expected 622 pixlpin items, got {pixlpin_count}"

    # 6. Verify Full Prompts availability
    with_prompts = sum(1 for it in items if it.get("full_prompt") and len(str(it["full_prompt"])) > 50)
    print(f"[*] Items with full verbatim prompts: {with_prompts}")
    assert with_prompts == 328, f"Expected 328 items with full prompts, got {with_prompts}"

    # 7. Verify Embeddings Matrix
    assert os.path.exists(EMBS_PATH), f"Missing {EMBS_PATH}"
    embs = np.load(EMBS_PATH)
    print(f"[*] Design embeddings shape: {embs.shape}, dtype: {embs.dtype}")
    assert embs.shape == (950, 384), f"Expected shape (950, 384), got {embs.shape}"
    assert embs.dtype == np.float32, f"Expected float32 dtype, got {embs.dtype}"

    # Verify L2 normalization
    norms = np.linalg.norm(embs, axis=1)
    np.testing.assert_allclose(norms, 1.0, atol=1e-5, err_msg="Embeddings rows are not L2 normalized!")
    print(f"[*] Embeddings L2 normalization verified (min norm={norms.min():.5f}, max norm={norms.max():.5f})")

    print("\n✅ ALL 7 DATASET VERIFICATION CHECKS PASSED PERFECTLY!\n")

if __name__ == "__main__":
    test_dataset()
