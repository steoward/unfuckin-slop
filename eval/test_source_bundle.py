"""Regression tests for lossless source delivery without network or model downloads."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from source_bundle import attach_source_bundles, open_source_bundle, safe_relative
from source_material import material_contract
import search_design_showcases as search


class SourceBundleTests(unittest.TestCase):
    def test_import_and_verify(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = b"export const Text = () => 'original';\r\n"
            asset = b"asset bytes"
            (root / "source.tsx").write_bytes(original)
            (root / "image.png").write_bytes(asset)
            row = {"id": "item", "source_url": "https://21st.dev/example/item"}
            manifest = root / "manifest.jsonl"
            manifest.write_text(json.dumps({"id": row["id"], "source_url": row["source_url"],
                "revision": "fixed-revision", "license": "MIT", "rights": "test fixture",
                "dependencies": ["react"], "files": [
                    {"path": "source.tsx", "target": "components/text.tsx"},
                    {"path": "image.png", "target": "public/image.png", "kind": "asset"},
                ]}), encoding="utf-8")
            attach_source_bundles(manifest, root, {"item": ("components", row)})
            with patch.dict("os.environ", {"UNFSLOP_SOURCE_ROOT": str(root)}):
                result = material_contract(row, "registry_instructions", full=True)
                self.assertEqual(result["tier"], "source_bundle")
                self.assertEqual(result["bundle_status"], "verified")
                self.assertEqual(result["files"][0]["content"].encode(), original)
                self.assertEqual(result["files"][0]["sha256"], hashlib.sha256(original).hexdigest())
                self.assertEqual(Path(result["assets"][0]["original_path"]).read_bytes(), asset)
                self.assertEqual(result["source_bundle"]["dependencies"], ["react"])
                self.assertFalse(result["complete_build_verified"])
                (root / "image.png").write_bytes(b"modified")
                with self.assertRaises(ValueError):
                    open_source_bundle(row["source_bundle"], root)
                result = material_contract(row, "registry_instructions", full=True)
                self.assertEqual(result["bundle_status"], "unavailable")
                self.assertEqual(result["files"], [])
                self.assertEqual(result["assets"], [])

    def test_rejects_traversal(self):
        for path in ("../outside", "/absolute", "D:/absolute", "..\\escape", "."):
            with self.subTest(path=path), self.assertRaises(ValueError):
                safe_relative(path)


class VisualRankingTests(unittest.TestCase):
    def test_ranks_pixels_not_lexical_similarity(self):
        rows = [dict(id="text", title="exact match exact", description="exact match", media=[]),
                dict(id="weak", title="exact match", description="exact match", media=[{"kind": "image"}]),
                dict(id="best", title="different title", description="different", media=[{"kind": "image"}])]
        class FakeIndex:
            text = np.ones((3, 2))
            def rank(self, indices, vector):
                return np.array([1., .99, -.2]), {1: (.1, 0, 0.), 2: (.9, 0, 0.)}
        def encoder(queries):
            return [np.ones(2)]
        with patch.object(search, "pack_visual", side_effect=lambda asset, time, score: {"similarity": score}):
            hits = search.rank_catalog("exact match", 3, rows, lambda: (encoder, FakeIndex()),
                                       allow_broad=True, visual_only=True)
        self.assertEqual([hit["id"] for hit in hits], ["best", "weak"])
        self.assertEqual(search.rank_catalog("exact match", 3, rows, lambda: (None, None),
                                            allow_broad=True, visual_only=True), [])


if __name__ == "__main__":
    unittest.main()
