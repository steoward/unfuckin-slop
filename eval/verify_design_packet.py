"""Exercise the installed design entry point from outside its source checkout."""
import json
from pathlib import Path
import os
import subprocess
import sys
from unittest.mock import patch


def run(binary, brief, pool="designs", env=None):
    command = [binary, "design", brief, "--pool", pool]
    result = subprocess.run(command, check=True, capture_output=True, encoding="utf-8", env=env)
    packet = json.loads(result.stdout)
    assert [rule["id"].split(".")[0] for rule in packet["craft"]] == ["imp", "apple"]
    assert all(rule["guidance"] for rule in packet["craft"])
    return packet["evidence"]


def main():
    binary = str(Path(sys.argv[1]).resolve())
    library = Path(binary).parent.parent / "design-library"
    sys.path.insert(0, str(library))
    import search_design_showcases as catalog

    briefs = [
        ("designs", "field recording sound archive audio library track list player"),
        ("components", "interactive audio waveform player scrubber"),
    ]
    for pool, query in briefs:
        evidence = run(binary, query, pool)
        assert (evidence["status"], evidence["backend"]) == ("ok", "hybrid"), evidence
        refs = evidence["references"]
        assert 1 <= len(refs) <= 3
        records = catalog.load_components() if pool == "components" else catalog.load_data()
        by_id = {r["id"]: r for r in records}
        for ref in refs:
            source = by_id[ref["id"]]
            assert ref["title"] == source["title"]
            assert ref["description"] == (source.get("description") or "")[:750]
            assert ref["blueprint_excerpt"] == ((source.get("full_prompt") or "")[:550] or None)
            assert ref["url"] == (source.get("source_url") or None)
            assert ref["video_url"] == (source.get("video_url") or None)
        print(pool, json.dumps(refs, ensure_ascii=True), flush=True)

    broad = run(binary, "build a website")
    assert broad["status"] == "needs_specific_query" and not broad["references"]
    missing = run(binary, briefs[0][1], env={**os.environ, "UNFSLOP_PYTHON": "missing-unfslop-python"})
    assert missing["status"] == "unavailable" and not missing["references"]
    with patch.object(catalog, "_load_semantic", return_value=(None, None)):
        lexical = catalog.reference_evidence("audio player", "designs")
        assert lexical["backend"] == "lexical" and lexical["references"]
    print("Verified hybrid designs and components, source fidelity, broad briefs, lexical and cards-only fallback.")


if __name__ == "__main__":
    main()
