"""Exercise real EmbeddingGemma 2 encoding against an optional visual asset."""
import argparse
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from semantic_index import DIM, query_vectors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path)
    args = parser.parse_args()
    embeddings = query_vectors(["swipeable card stack", "dark analytics dashboard"], args.reference)
    assert embeddings.shape == (2, DIM)
    np.testing.assert_allclose(np.linalg.norm(embeddings, axis=1), 1.0, atol=1e-3)
    assert np.isfinite(embeddings).all()
    print("EmbeddingGemma 2 produced normalized 768-dimensional vectors.")


if __name__ == "__main__":
    main()
