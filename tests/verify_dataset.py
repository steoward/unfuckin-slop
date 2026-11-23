"""Verify catalog contents and vector layout for the committed snapshots."""
from collections import Counter
import json
from pathlib import Path

import numpy as np

CATALOG = Path(__file__).resolve().parents[1] / "design_showcases"


def verify_catalog(meta_name, vectors_name, sources):
    records = json.loads((CATALOG / meta_name).read_text(encoding="utf-8"))
    assert Counter(row["source_site"] for row in records) == sources
    assert len({row["id"] for row in records}) == len(records)
    vectors = np.load(CATALOG / vectors_name)
    assert vectors.shape == (len(records), 384) and vectors.dtype == np.float32
    np.testing.assert_allclose(np.linalg.norm(vectors, axis=1), 1.0, atol=1e-5)
    return records


def test_dataset():
    designs = verify_catalog("showcases_meta.json", "design_embeddings.npy",
                             {"pixlpin.com": 622, "motionsites.ai": 328})
    verify_catalog("components_meta.json", "component_embeddings.npy",
                   {"21st.dev": 9698, "skiper-ui.com": 37})
    assert sum(bool(row.get("video_url")) for row in designs) >= 800
    assert sum(bool(row.get("is_3d")) for row in designs) >= 300
    assert sum(bool(row.get("is_liquid_glass")) for row in designs) >= 70
    assert all(row["full_prompt"] for row in designs if row["source_site"] == "motionsites.ai")
    print("Verified both catalogs and their embedding arrays.")


if __name__ == "__main__":
    test_dataset()
