import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import semantic_index as semantic


class FixtureEncoder:
    def __init__(self):
        self.tokenizer = self
        self.calls = []

    def encode(self, text, *, add_special_tokens, truncation, verbose):
        assert not (add_special_tokens or truncation or verbose)
        return text.split()

    def decode(self, tokens, *, skip_special_tokens):
        assert skip_special_tokens
        return " ".join(tokens)

    def encode_document(self, texts, *, normalize_embeddings, batch_size, show_progress_bar):
        assert normalize_embeddings
        self.calls.append(list(texts))
        vectors = np.zeros((len(texts), semantic.DIM), dtype=np.float32)
        for vector, text in zip(vectors, texts):
            vector[0 if text in {"needle", "Metadata match"} else 1] = 1
        return vectors


class PayloadRetrievalTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        self.addCleanup(semantic.open_index.cache_clear)
        self.enterContext(patch.object(semantic, "DATA_DIR", directory))
        self.enterContext(patch.object(semantic, "model_key", return_value="fixture"))
        self.catalog = directory / "showcases_meta.json"
        self.rows = [
            {"id": "first", "title": "Payload match", "full_prompt": "word " * 384 + "needle"},
            {"id": "second", "title": "Metadata match"},
            {"id": "third", "title": "Other", "full_prompt": "unrelated"},
        ]
        self.save_catalog()
        self.query = np.eye(1, semantic.DIM, dtype=np.float32)[0]

    def save_catalog(self):
        self.catalog.write_text(json.dumps(self.rows), encoding="utf-8")

    def test_build_roundtrip_and_rank_payload_and_metadata(self):
        encoder = FixtureEncoder()
        with patch.object(semantic, "load_encoder", return_value=encoder):
            semantic.build_index("showcases", batch_size=2)
        self.assertEqual(encoder.calls[1:], [["word " * 383 + "word", "needle"], ["unrelated"]])
        index = semantic.open_index("showcases")
        np.testing.assert_array_equal(index.chunk_owners, [0, 0, 2])
        scores, visual = index.rank([2, 0, 1], self.query)
        np.testing.assert_array_equal(scores, [0, 1, 1])
        self.assertEqual(visual, {})

        self.rows[0]["full_prompt"] = "mutated"
        self.save_catalog()
        semantic.open_index.cache_clear()
        with self.assertRaisesRegex(ValueError, "rebuild"):
            semantic.open_index("showcases")

    def test_legacy_index_keeps_metadata_ranking(self):
        encoder = FixtureEncoder()
        text = encoder.encode_document([row["title"] for row in self.rows],
                                       normalize_embeddings=True, batch_size=3, show_progress_bar=False)
        semantic.save_index(
            semantic.index_path("showcases"), model="fixture", corpus=semantic.row_digest(self.rows),
            text=text, visual=np.empty((0, semantic.DIM)), owners=[], asset_indices=[], starts=[],
        )
        index = semantic.open_index("showcases")
        np.testing.assert_array_equal(index.rank_text([0, 1, 2], self.query), [0, 1, 0])
        self.assertIsNone(index.chunks)

    def test_catalog_without_payloads_has_empty_chunk_matrix(self):
        chunks, owners = semantic.encode_payloads(FixtureEncoder(), [self.rows[1]], batch_size=2)
        self.assertEqual(chunks.shape, (0, semantic.DIM))
        self.assertEqual(owners.shape, (0,))


if __name__ == "__main__":
    unittest.main()
