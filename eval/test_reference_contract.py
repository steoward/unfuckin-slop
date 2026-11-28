"""Exercise the reference contract through the library and plan commands."""

from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from eval.verify_design_packet import PNG, record


ROOT = Path(__file__).resolve().parents[1]


class ReferenceContractTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.prompt = " Preserve both columns.\r\n" + "♪" * 600 + "\n"
        self.video = "https://cdn.example.com/exact.mp4?version=2&size=large"
        self.source = "https://motionsites.ai/?prompt=sound-atlas"
        self.registry = "https://21st.dev/r/example/nav"
        self.preview = self.root / "original.png"
        self.preview.write_bytes(PNG)
        self.checksum = sha256(PNG).hexdigest()
        design = record("sound-atlas", "Sound Atlas", "motionsites.ai", "Hero", "", self.prompt)
        design.update(source_url=self.source, video_url=self.video, media=[
            {"kind": "image", "path": self.preview.name, "sha256": self.checksum, "rights": "Test fixture"}
        ])
        component = record("nav", "Navbar", "21st.dev", "Navigation", "",
                           f'Install: npx shadcn@latest add "{self.registry}?api_key=$API_KEY_21ST"')
        for pool, rows in (("showcases", [design]), ("components", [component])):
            (self.root / f"{pool}_meta.json").write_text(json.dumps(rows), encoding="utf-8")

    def run_library(self, *arguments):
        env = {**os.environ, "UNFSLOP_LIBRARY_DATA": str(self.root), "UNFSLOP_MEDIA_ROOT": str(self.root)}
        return json.loads(subprocess.check_output(
            [sys.executable, str(ROOT / "build_library.py"), *arguments], cwd=ROOT, env=env, encoding="utf-8",
        ))

    def test_selected_reference_preserves_evidence_and_requires_comparison(self):
        plan = self.run_library("plan", "sound-atlas")
        selected = plan["blueprint"]["selected"]
        contract = selected["reference_contract"]
        self.assertEqual(contract["reference_id"], "sound-atlas")
        self.assertEqual(contract["urls"], {"source": self.source, "video": self.video})
        self.assertEqual(selected["delivery"]["payload"], self.prompt)
        self.assertEqual(selected["inspection"]["preview"]["sha256"], self.checksum)
        self.assertEqual(contract["status"], "comparison_required")
        self.assertTrue(contract["comparison_required"])
        self.assertEqual(contract["missing_evidence"], [])
        hero = next(section for section in plan["sections"] if section["name"] == "hero")
        self.assertTrue(hero["uses_blueprint"])
        self.assertEqual(hero["selected"]["id"], contract["reference_id"])

    def test_changed_asset_and_unresolved_registry_block_fidelity(self):
        self.preview.write_bytes(PNG + b"changed")
        design, registry = self.run_library("library", "--record", "sound-atlas", "--record", "nav")["items"]
        self.assertEqual(design["reference_contract"]["status"], "missing_evidence")
        self.assertEqual(design["reference_contract"]["missing_evidence"], ["verified_original_visual_evidence"])
        self.assertEqual(registry["reference_contract"]["urls"]["registry"], self.registry)
        self.assertIn("verified_registry_source", registry["reference_contract"]["missing_evidence"])
        self.assertEqual(registry["delivery"]["files"], [])

    def test_verified_image_does_not_supply_missing_source_or_payload(self):
        catalog = self.root / "showcases_meta.json"
        designs = json.loads(catalog.read_text(encoding="utf-8"))
        designs[0].update(full_prompt="", source_url="")
        catalog.write_text(json.dumps(designs), encoding="utf-8")
        selected = self.run_library("library", "--record", "sound-atlas")["items"][0]
        contract = selected["reference_contract"]
        self.assertEqual(contract["visual_evidence_status"], "verified")
        self.assertEqual(contract["status"], "missing_evidence")
        self.assertEqual(contract["missing_evidence"], ["original_source_url", "full_payload"])


if __name__ == "__main__":
    unittest.main()
