import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from delivery_packet import export_packet


class DeliveryTests(unittest.TestCase):
    def test_export_is_lossless_and_non_overwriting(self):
        text = "export const a = 'é';\r\n"
        digest = hashlib.sha256(text.encode()).hexdigest()
        packet = {"query": "carousel", "items": [{"id": "fixture", "source": "skiper-ui.com",
                    "url": "https://example.org/source", "score": .7,
                    "delivery": {"tier": "source_snapshot", "payload": text, "payload_sha256": digest,
                                 "files": [{"path": "widget.tsx", "content": text, "sha256": digest}]}}]}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "output"
            export_packet(packet, root)
            self.assertEqual((root / "fixture/source/widget.tsx").read_bytes(), text.encode())
            manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["records"][0]["files"][1]["sha256"], digest)
            self.assertFalse(manifest["complete_build_verified"])
            with self.assertRaises(FileExistsError):
                export_packet(packet, root)
            packet["items"][0]["delivery"]["files"][0]["path"] = "../escape"
            with self.assertRaises(ValueError):
                export_packet(packet, root.with_name("unsafe"))
            self.assertFalse(root.with_name("unsafe").exists())

if __name__ == "__main__":
    unittest.main()
