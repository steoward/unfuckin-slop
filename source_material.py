"""Lossless source delivery and verifiable visual reference sheets.

An embedding selects a catalog key; the source, not the embedding, supplies the
implementation. Never label a prompt, registry pointer or video as source code.
"""
import hashlib
import os
from pathlib import Path
import re
import subprocess
from tempfile import NamedTemporaryFile, TemporaryDirectory

from semantic_index import DATA_DIR, VISUAL_WINDOW_SECONDS, media_path
from source_bundle import open_source_bundle


SOURCE_FILE = re.compile(r"(?m)^--- file: ([^\r\n]+?) ---[ \t]*\r?\n```[^\r\n]*\r?\n(.*?)^```[ \t]*\r?$", re.DOTALL)


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def source_files(body):
    """Extract named files without executing, writing or changing the stored text."""
    return [{"path": match[1], "content": match[2], "sha256": digest(match[2])}
            for match in SOURCE_FILE.finditer(body)]


def material_contract(row, kind, full=False):
    body = row.get("full_prompt") or ""
    files = source_files(body) if kind == "component_source_snapshot" else []
    bundle = row.get("source_bundle")
    if bundle:
        tier = "source_bundle"
    elif files:
        tier = "source_snapshot"
    elif kind == "design_prompt" and body.strip():
        tier = "build_specification"
    elif kind == "registry_instructions" and body.strip():
        tier = "registry_pointer"
    elif row.get("media"):
        tier = "visual_reference"
    else:
        tier = "description_only"
    result = {
        "tier": tier,
        "payload_sha256": digest(body) if body else None,
        "payload_bytes": len(body.encode("utf-8")),
        "source_file_count": (sum(item["kind"] == "text" for item in bundle["files"]) if bundle else len(files)),
        "requires_reconstruction": tier not in {"source_snapshot", "source_bundle"},
        "complete_build_verified": False,
        "license": bundle["license"] if bundle else row.get("license") or None,
        "media_count": len(row.get("media", [])),
    }
    if full:
        result.update(payload=body or None, files=files)
    if bundle:
        result["source_bundle"] = {key: bundle[key] for key in ("source_url", "revision", "license", "rights", "dependencies")}
        if full:
            root = Path(os.environ.get("UNFSLOP_SOURCE_ROOT", DATA_DIR / "sources"))
            try:
                files, assets = open_source_bundle(bundle, root)
                result.update(files=files, assets=assets, bundle_status="verified")
            except (OSError, ValueError) as exc:
                result.update(files=[], assets=[], bundle_status="unavailable", bundle_error=str(exc),
                              requires_reconstruction=True)
    return result


def reference_sheet(asset, start):
    """Validate original bytes and create a contact sheet of a matched window.

    The original file remains untouched. Only selected/full records call this;
    catalog browsing never decodes or hashes every asset.
    """
    path = media_path(asset)
    with path.open("rb") as stream:
        checksum = hashlib.file_digest(stream, "sha256").hexdigest()
    if checksum != asset["sha256"]:
        raise ValueError(f"Original asset changed: {path.name}")
    if asset["kind"] == "image":
        return {"path": str(path), "sha256": checksum, "kind": "original_image"}
    from PIL import Image, ImageDraw
    start = max(0.0, float(start))
    cache = Path(os.environ.get("UNFSLOP_REFERENCE_CACHE", DATA_DIR / ".reference-cache"))
    cache.mkdir(parents=True, exist_ok=True)
    key = f"{checksum}-{int(start * 1000)}-v1"
    target = cache / f"{key}.png"
    if not target.exists():
        frames = []
        with TemporaryDirectory(prefix="unfslop-preview-") as temp:
            for offset in range(0, VISUAL_WINDOW_SECONDS, 2):
                timestamp = start + offset
                frame = Path(temp) / f"{offset}.png"
                subprocess.run(["ffmpeg", "-v", "error", "-ss", str(timestamp), "-i", str(path),
                                "-frames:v", "1", "-vf", "scale=640:360:force_original_aspect_ratio=decrease",
                                "-y", str(frame)], check=True, capture_output=True)
                if frame.exists():
                    with Image.open(frame) as pixels:
                        frames.append((timestamp, pixels.convert("RGB")))
            if not frames:
                raise ValueError("No frames in selected video window")
            sheet = Image.new("RGB", (1280, 388 * ((len(frames) + 1) // 2)), "#161616")
            draw = ImageDraw.Draw(sheet)
            for i, (timestamp, frame) in enumerate(frames):
                x, y = (i % 2) * 640, (i // 2) * 388
                sheet.paste(frame, (x + (640 - frame.width) // 2, y + (360 - frame.height) // 2))
                draw.text((x + 8, y + 365), f"{timestamp:.1f}s (requested seek)", fill="white")
            with NamedTemporaryFile(dir=cache, suffix=".png", delete=False) as output:
                temporary = Path(output.name)
            try:
                sheet.save(temporary)
                temporary.replace(target)
            finally:
                temporary.unlink(missing_ok=True)
    return {"path": str(target.resolve()), "sha256": checksum, "kind": "video_contact_sheet",
            "window_start": start, "window_seconds": VISUAL_WINDOW_SECONDS}


def full_evidence(row, evidence):
    if not evidence:
        return {"status": "missing", "reason": "No local visual asset; source or registry may be opened separately."}
    for asset in row.get("media", []):
        try:
            path = media_path(asset)
        except OSError:
            continue
        if str(path) != evidence["path"]:
            continue
        try:
            return {"status": "verified", "preview": reference_sheet(asset, evidence.get("seconds", 0))}
        except (OSError, ValueError, subprocess.SubprocessError, ImportError) as exc:
            return {"status": "unavailable", "reason": str(exc)}
    return {"status": "unavailable", "reason": "Selected asset no longer resolves in the catalog."}
