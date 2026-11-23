"""Exercise the installed design entry point from outside its source checkout."""
import json
from pathlib import Path
import os
import subprocess
import sys
from unittest.mock import patch


def run(binary, brief, pool="designs", env=None, source=None):
    command = [binary, "design", brief, "--pool", pool]
    if source:
        command += ["--source", source]
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
            assert ref["blueprint_excerpt"] == ((source.get("full_prompt") or "").strip()[:550] or None)
            assert ref["url"] == (source.get("source_url") or None)
            assert ref["video_url"] == (source.get("video_url") or None)
            assert ref["material"]["characters"] == len((source.get("full_prompt") or "").strip())
        lookup = subprocess.run([binary, "design", "--pool", pool, "--record", refs[0]["id"]],
                                check=True, capture_output=True, encoding="utf-8")
        assert json.loads(lookup.stdout) == by_id[refs[0]["id"]]
        print(pool, [ref["id"] for ref in refs], flush=True)
    filtered = catalog.reference_evidence("", "designs", filter_3d=True, limit=1)
    assert filtered["backend"] == "catalog_filter" and len(filtered["references"]) == 1
    empty = catalog.reference_evidence("archive", "designs", category_filter="zzz-no-category")
    assert empty["status"] == "no_matches" and not empty["references"]
    sample = {"title": "Plain index", "description": "A quiet list."}
    formatted = catalog.format_full_blueprint(sample)
    assert "A quiet list." in formatted and "no source blueprint" in formatted
    assert "Tailwind" not in formatted

    sources = [
        ("designs", "motionsites.ai", "3d-character-studio", "design_prompt"),
        ("components", "skiper-ui.com", "skiper-skiper48", "component_source_snapshot"),
        ("components", "21st.dev", "21st-aurora-ribbons", "registry_instructions"),
    ]
    for pool, source, record_id, kind in sources:
        evidence = run(binary, record_id, pool, source=source)
        assert evidence["backend"] == "catalog_exact" and evidence["exact_matches"] == 1
        ref, = evidence["references"]
        assert (ref["id"], ref["source"], ref["material"]["kind"]) == (record_id, source, kind)
        assert ref["material"]["excerpt_truncated"] == (kind != "registry_instructions")
    wrong = run(binary, "https://skiper-ui.com/v1/unknown-record", "components", source="skiper-ui.com")
    assert wrong["status"] == "no_matches"
    same_title = [{"id": "a", "title": "Shared"}, {"id": "b", "title": "Shared"}]
    assert [r["id"] for r in catalog.exact_references("shared", same_title)] == ["a", "b"]

    broad = run(binary, "build a website")
    assert broad["status"] == "needs_specific_query" and not broad["references"]
    missing = run(binary, briefs[0][1], env={**os.environ, "UNFSLOP_PYTHON": "missing-unfslop-python"})
    assert missing["status"] == "unavailable" and not missing["references"]
    with patch.object(catalog, "_load_semantic", return_value=(None, None)):
        lexical = catalog.reference_evidence("audio waveform controls on a playback timeline", "designs")
        assert lexical["backend"] == "lexical" and lexical["references"]
    print("Verified hybrid designs and components, source fidelity, broad briefs, lexical and cards-only fallback.")


if __name__ == "__main__":
    main()
