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



def run_json(binary, *args):
    return json.loads(subprocess.check_output([binary, *args], encoding="utf-8"))


def verify_build_library(binary, catalog):
    records = catalog.load_data() + catalog.load_components()
    by_id = {row["id"]: row for row in records}
    page = run_json(binary, "library", "--limit", "2")
    assert page["total"] == len(by_id) and page["next_offset"] == 2
    tail = run_json(binary, "library", "--offset", str(page["total"] - 1))
    assert len(tail["items"]) == 1 and tail["next_offset"] is None
    filtered = run_json(binary, "library", "--source", "motionsites.ai", "--category", "Footer")
    assert filtered["items"] and all(
        row["source"] == "motionsites.ai" and row["category"] == "Footer"
        for row in filtered["items"]
    )
    ranked = run_json(binary, "library", "swipeable card stack", "--source", "skiper-ui.com")
    assert ranked["backends"] == {"components": "hybrid"}
    assert "skiper-skiper48" in [row["id"] for row in ranked["items"][:5]]

    ids = ["3d-character-studio", "skiper-skiper48", "21st-aurora-ribbons"]
    opened = run_json(binary, "library", *(arg for record_id in ids for arg in ("--record", record_id)))
    assert [item["record"] for item in opened["items"]] == [by_id[record_id] for record_id in ids]
    assert [item["use"]["action"] for item in opened["items"]] == [
        "adapt_prompt", "adapt_source", "install_registry",
    ]
    registry = opened["items"][-1]["use"]
    assert registry["credential_env"] == "API_KEY_21ST" and "?" not in registry["registry_url"]

    plan = run_json(binary, "plan", "Portable field recorder for hikers with a microphone comparison and reservation")
    assert plan["status"] == "ok"
    assert plan["blueprint"]["backends"] == {"designs": "hybrid"}
    assert plan["blueprint"]["selected"]["use"]["action"] == "adapt_prompt"
    assert [part["name"] for part in plan["sections"]] == [
        "navigation", "hero", "features", "call-to-action", "footer",
    ]
    for part in plan["sections"]:
        assert part["selected"]["id"] in by_id and part["selected"]["use"]["instruction"]
    custom = run_json(binary, "plan", "Photo archive with swipe interaction",
                      "--section", "carousel=skiper-skiper48", "--full", "--local")
    section, = custom["sections"]
    assert section["backends"]["components"] == "catalog_exact"
    assert section["selected"]["record"] == by_id["skiper-skiper48"]
    assert custom["blueprint"]["selected"]["record"]["full_prompt"]
    print("Verified library pagination, hybrid ranking, full source reads and build plans.", flush=True)

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
    assert not catalog.search("build a website")
    assert all("design_system" not in row for row in catalog.search("liquid glass hero", limit=3))
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
    verify_build_library(binary, catalog)


if __name__ == "__main__":
    main()
