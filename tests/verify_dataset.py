"""Verify a private EmbeddingGemma 2 catalog and any built indexes."""
from collections import Counter
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from semantic_index import DIM, canonical_rows, media_path, open_index


def main():
    all_ids = set()
    for pool in ("showcases", "components"):
        rows = canonical_rows(pool)
        for row in rows:
            assert row["id"] not in all_ids, row["id"]
            all_ids.add(row["id"])
            for media in row.get("media", []):
                assert media_path(media).is_file()
        index = open_index(pool)
        if index is not None:
            assert index.text.shape == (len(rows), DIM)
            assert index.visual.shape[1] == DIM
            assert len(index.visual) == len(index.owners) == len(index.asset_indices) == len(index.starts)
            assert all(0 <= idx < len(rows) for idx in index.owners)
            np.testing.assert_allclose(np.linalg.norm(index.text, axis=1), 1, atol=1e-3)
            np.testing.assert_allclose(np.linalg.norm(index.visual, axis=1), 1, atol=1e-3)
        print(pool, dict(Counter(row["source_site"] for row in rows)))


if __name__ == "__main__":
    main()
