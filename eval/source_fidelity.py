"""Measure finding known references and inspect the payloads the agent receives."""
import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import search_design_showcases as catalog

CASES = [
    ("motionsites.ai", "3d-character-studio", "mouse controls a character video timeline in a creative studio hero"),
    ("motionsites.ai", "facet-glass-hero", "smoked glass shards floating in a black real-time material studio"),
    ("motionsites.ai", "medusa-jellyfish-hero", "take apart a robotic jellyfish piece by piece in a simulator"),
    ("motionsites.ai", "lifeline-sun-hero", "timeline for the life stages of a glowing sun on black"),
    ("skiper-ui.com", "skiper-skiper48", "stacked picture cards you drag between with optional autoplay"),
    ("skiper-ui.com", "skiper-skiper65", "developer overlay showing active Tailwind responsive breakpoint"),
    ("skiper-ui.com", "skiper-skiper39", "canvas crowd simulation with moving particles and fluid dynamics"),
    ("skiper-ui.com", "skiper-skiper49", "inverted coverflow with reversed perspective and transitions"),
    ("21st.dev", "21st-aurora-ribbons", "react three fiber background with silky aurora ribbons in theme colors"),
    ("21st.dev", "21st-error9", "404 error that strikes through the bad path and suggests the nearest page"),
    ("21st.dev", "21st-turntable", "drag an isometric block turntable that snaps to quarter turns"),
    ("21st.dev", "21st-8bit-accordion", "retro pixel panel accordion with thick dashed borders"),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, help="Optional saved copy of the previous search script")
    args = parser.parse_args()
    if args.baseline:
        spec = importlib.util.spec_from_file_location("previous_catalog", args.baseline)
        previous = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(previous)
        for name in ("META_PATH", "COMPONENTS_META_PATH"):
            if hasattr(catalog, name):
                setattr(previous, name, getattr(catalog, name))

    rows_by_pool = {"designs": catalog.load_data(), "components": catalog.load_components()}
    source_to_pool = {s: p for p, sources in catalog.REFERENCE_SOURCES.items() for s in sources}
    inventory = {}
    for pool, rows in rows_by_pool.items():
        for row in rows:
            source = row["source_site"]
            material = catalog.pack_reference(row)["material"]
            body = row.get("full_prompt") or ""
            counts = inventory.setdefault(source, Counter())
            counts.update({"records": 1, "with_media_url": bool(row.get("video_url")),
                           "with_text": bool(body.strip()), "excerpt_truncated": material["excerpt_truncated"],
                           "with_install_hint": "Install:" in body,
                           "with_code_marker": bool(re.search(r"(?m)^\s*(?:import\s+.+from\s+|export\s+(?:default|function|const|class)\s+)", body))})

    outcomes = {}
    for source, record_id, paraphrase in CASES:
        pool = source_to_pool[source]
        record = next(row for row in rows_by_pool[pool] if row["id"] == record_id)
        for kind, query in [("title", record["title"]), ("url", record["source_url"]),
                            ("paraphrase", paraphrase)]:
            comparisons = [("current", catalog.reference_evidence(query, pool)),
                           ("source_filtered", catalog.reference_evidence(query, pool, source_filter=source))]
            if args.baseline:
                comparisons.insert(0, ("previous", previous.reference_evidence(query, pool)))
            for arm, packet in comparisons:
                assert packet["backend"] in ("catalog_exact", "gemma2_text", "gemma2_multimodal", "lexical"), packet
                ref_ids = [ref["id"] for ref in packet["references"]]
                counts = outcomes.setdefault(source, {}).setdefault(arm, {}).setdefault(kind, Counter())
                counts.update({"cases": 1, "top1": bool(ref_ids and ref_ids[0] == record_id),
                               "top3": record_id in ref_ids})
            for ref in comparisons[-1][1]["references"]:
                assert ref["source"] == source, ref
    print(json.dumps({"inventory": inventory, "retrieval": outcomes}, indent=2))


if __name__ == "__main__":
    main()
