"""Build a private catalog from supplied source bundles and local media."""
import argparse
from collections import Counter
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from visual_annotations import validate_annotation

BUNDLES = {
    "motionsites-free-prompts.txt": ("motionsites.ai", "showcases"),
    "skiper-ui-free-prompts.txt": ("skiper-ui.com", "components"),
    "21st-dev-free-prompts.txt": ("21st.dev", "components"),
}
ENTRY = re.compile(
    r"^={50,}\n\[\d+\] (?P<title>[^\n]+)\n"
    r"(?P<header>(?:(?!^-{50,}$)[^\n]*\n)+)^-{50,}\n",
    re.MULTILINE,
)
TRAILER = re.compile(r"\n(?:#{50,}\n# |={50,}\nEND OF COLLECTION)")
VIDEO = re.compile(r"https?://[^\s\"'<>\)\x60]+?\.mp4", re.IGNORECASE)
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_SUFFIXES = {".mp4", ".webm", ".mov", ".mkv"}
EXTRA_SOURCES = {"collectui.com", "pixlpin.com"}


def header_value(header, name):
    match = re.search(rf"(?:^|\|\s*){re.escape(name)}:\s*([^|\n]+)", header, re.MULTILINE)
    return match.group(1).strip() if match else ""


def bundle_rows(path, source, pool, archived):
    data = path.read_text(encoding="utf-8-sig")
    entries = list(ENTRY.finditer(data))
    count = re.search(r"^Total free [^:]+:\s*([\d,]+)", data, re.MULTILINE)
    if not entries or (count and len(entries) != int(count[1].replace(",", ""))):
        raise ValueError(f"Unexpected entry count in {path}: {len(entries)}")
    for index, match in enumerate(entries):
        header = match["header"]
        end = entries[index + 1].start() if index + 1 < len(entries) else len(data)
        body = TRAILER.split(data[match.end():end], maxsplit=1)[0].strip()
        url = header_value(header, "Source")
        if urlparse(url).hostname not in {source, f"www.{source}"} or not body:
            raise ValueError(f"Missing payload or invalid source in {path}: {match['title']}")
        row = dict(archived.get(url, {}))
        if not row:
            slug = parse_qs(urlparse(url).query).get("prompt", [urlparse(url).path.rsplit("/", 1)[-1]])[0]
            prefix = {"21st.dev": "21st-", "skiper-ui.com": "skiper-"}.get(source, "")
            row["id"] = f"{prefix}{slug}"
        title = match["title"].strip()
        category = header_value(header, "Category") or header_value(header, "Collection")
        about = header_value(header, "About") or body.split("\n", 1)[0].strip("> ")
        install = header_value(header, "Install")
        if install and source == "21st.dev":
            # Keep the canonical instruction where the agent can find it.
            body += f"\n\nInstall: {install}"
        row.update(
            title=title, source_site=source, source_url=url,
            category=category, type=header_value(header, "Type") or "component",
            description=row.get("description") or about,
            full_prompt=body, video_url=(VIDEO.search(body)[0] if pool == "showcases" and VIDEO.search(body)
                                         else row.get("video_url")),
        )
        for field, label in (("author", "Author"), ("license", "License"), ("npm_deps", "npm dependencies")):
            if value := header_value(header, label):
                row[field] = value
        row["tags"] = [tag.strip() for tag in header_value(header, "Tags").split(",") if tag.strip()]
        yield row


def file_digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def attach_media(path, media_root, rows):
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        relative = Path(item["path"])
        local = (media_root / relative).resolve()
        if relative.is_absolute() or not local.is_relative_to(media_root) or not local.is_file():
            raise ValueError(f"Media file must exist under the media root: {relative}")
        if local.suffix.lower() in VIDEO_SUFFIXES:
            kind = "video"
        elif local.suffix.lower() in IMAGE_SUFFIXES:
            kind = "image"
        else:
            raise ValueError(f"Unsupported media file: {local}")
        if not item.get("rights"):
            raise ValueError(f"Record {item['id']} needs a source or license note")
        if item["id"] not in rows:
            source = urlparse(item["source_url"]).hostname
            if source not in EXTRA_SOURCES:
                raise ValueError(f"Unknown record or unsupported source: {item['id']}")
            rows[item["id"]] = ("showcases", {
                "id": item["id"], "title": item["title"], "source_site": source,
                "source_url": item["source_url"], "description": item["description"],
                "category": item.get("category", ""), "type": item.get("type", "showcase"),
            })
        _, row = rows[item["id"]]
        checksum = file_digest(local)
        assets = row.setdefault("media", [])
        asset = next((entry for entry in assets if entry["sha256"] == checksum), None)
        if asset is None:
            asset = {"kind": kind, "path": relative.as_posix(), "sha256": checksum, "rights": item["rights"]}
            assets.append(asset)
        if "annotation" in item:
            report = item["annotation"]
            if not isinstance(report, dict):
                raise ValueError(f"Annotation for {item['id']} must be a JSON object")
            duration = 0.0
            if kind == "video":
                probe = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                                                 "format=duration", "-of", "json", str(local)])
                duration = float(json.loads(probe)["format"]["duration"])
            asset["annotation"] = validate_annotation(report, checksum, row["id"], duration)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompts", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--archive", type=Path, help="Existing private catalog metadata and stable IDs")
    parser.add_argument("--media-manifest", type=Path, help="JSON Lines of authorized local assets")
    parser.add_argument("--media-root", type=Path)
    args = parser.parse_args()
    if bool(args.media_manifest) != bool(args.media_root):
        parser.error("--media-manifest and --media-root must be used together")
    archived = {}
    if args.archive:
        for pool in ("showcases", "components"):
            path = args.archive / f"{pool}_meta.json"
            for row in json.loads(path.read_text(encoding="utf-8")):
                archived[row["source_url"]] = row
    rows = {}
    for name, (source, pool) in BUNDLES.items():
        for row in bundle_rows(args.prompts / name, source, pool, archived):
            if row["id"] in rows and source == "21st.dev":
                row["id"] += "-" + hashlib.sha256(row["source_url"].encode()).hexdigest()[:10]
            if row["id"] in rows:
                raise ValueError(f"Duplicate record ID: {row['id']}")
            rows[row["id"]] = (pool, row)
    for row in archived.values():
        if row["source_site"] in EXTRA_SOURCES:
            rows.setdefault(row["id"], ("showcases", row))
    if args.media_manifest:
        attach_media(args.media_manifest, args.media_root.resolve(), rows)
    args.output.mkdir(parents=True, exist_ok=True)
    for pool in ("showcases", "components"):
        selected = [row for group, row in rows.values() if group == pool]
        target = args.output / f"{pool}_meta.json"
        target.write_text(json.dumps(selected, ensure_ascii=False), encoding="utf-8")
    coverage = {
        "records": dict(Counter(row["source_site"] for _, row in rows.values())),
        "remote_video_references": dict(Counter(row["source_site"] for _, row in rows.values()
                                               if row.get("video_url"))),
        "assets": dict(Counter(asset["kind"] for _, row in rows.values() for asset in row.get("media", []))),
        "annotated_assets": sum("annotation" in asset for _, row in rows.values() for asset in row.get("media", [])),
    }
    (args.output / "coverage.json").write_text(json.dumps(coverage, indent=2), encoding="utf-8")
    print(json.dumps(coverage, indent=2))


if __name__ == "__main__":
    main()
