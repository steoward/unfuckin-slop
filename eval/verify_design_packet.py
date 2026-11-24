"""Test the installed CLI with a small public-safe catalog."""
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


def record(key, title, source, category, description, body=""):
    return dict(id=key, title=title, source_site=source, source_url=f"https://{source}/{key}",
                category=category, type="hero" if category == "Hero" else category.lower(),
                description=description, full_prompt=body)


def test_cli(binary, location):
    designs = [
        record("sound-atlas", "Sound Atlas", "motionsites.ai", "Hero",
               "Browse field recordings with a waveform timeline",
               "Build a two-column recorder page with a waveform timeline."),
        record("plain-footer", "Plain Footer", "motionsites.ai", "Footer",
               "Links and contact information in a small site footer", "Use a footer nav."),
    ]
    components = [
        record("sample-swipe", "Swiping Cards", "skiper-ui.com", "Carousel",
               "Drag stacked photo cards horizontally",
               "export const Cards = () => <section>Cards</section>;"),
        record("sample-nav", "Navbar", "21st.dev", "Navigation",
               "Responsive navigation with mobile menu",
               'Install: npx shadcn@latest add "https://21st.dev/r/example/nav?api_key=$API_KEY_21ST"'),
    ]
    for name, rows in (("showcases", designs), ("components", components)):
        (location / f"{name}_meta.json").write_text(json.dumps(rows), encoding="utf-8")
    env = {**os.environ, "UNFSLOP_LIBRARY_DATA": str(location)}

    def run(*args):
        return json.loads(subprocess.check_output([binary, *args], env=env, encoding="utf-8"))

    page = run("library", "--limit", "2")
    assert page["total"] == 4 and page["next_offset"] == 2
    assert run("library", "--offset", "2")["next_offset"] is None
    hit = run("library", "stacked photo cards", "--source", "skiper-ui.com")
    assert hit["backends"] == {"components": "lexical"}
    assert hit["items"][0]["id"] == "sample-swipe"
    items = run("library", "--record", "sound-atlas", "--record", "sample-nav")["items"]
    assert [item["record"] for item in items] == [designs[0], components[1]]
    assert items[1]["use"]["registry_url"] == "https://21st.dev/r/example/nav"
    plan = run("plan", "Field recordings with a waveform timeline",
               "--section", "carousel=sample-swipe", "--full")
    assert plan["status"] == "ok" and plan["blueprint"]["selected"]["id"] == "sound-atlas"
    assert plan["sections"][0]["selected"]["record"] == components[0]
    evidence = run("design", "sound-atlas")["evidence"]
    assert evidence["backend"] == "catalog_exact" and evidence["references"][0]["visual_evidence"] is None
    print("Verified browse, exact and lexical retrieval, source payloads and section planning.")


if __name__ == "__main__":
    with TemporaryDirectory() as directory:
        test_cli(str(Path(sys.argv[1]).resolve()), Path(directory))
