"""Materialize a selected reference as immutable, inspectable local files."""
import hashlib
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

from source_bundle import safe_relative, sha256_file
from semantic_index import verified_media_path


def export_packet(packet, destination):
    """No execution, network access or overwriting. Export only verified bytes."""
    destination = Path(destination).resolve()
    if destination.exists():
        raise FileExistsError(f"Export destination already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    entries = packet.get("items", [])
    if "blueprint" in packet:
        entries = [slot["selected"] for slot in [packet["blueprint"], *packet["sections"]]
                   if slot.get("selected") and not slot.get("uses_blueprint")]
    if not entries:
        raise ValueError("No selected references to export")
    records = []
    with TemporaryDirectory(prefix=".delivery-", dir=destination.parent) as temp:
        staging = Path(temp) / "packet"
        staging.mkdir()
        for entry in entries:
            reference = str(safe_relative(entry["id"]))
            if "/" in reference:
                raise ValueError("Record ID must be a single path segment")
            root = staging / reference
            if root.exists():
                continue
            root.mkdir()
            delivery = entry["delivery"]
            files = []
            targets = set()
            def write_checked(target, content, checksum):
                relative = safe_relative(target)
                key = str(relative).casefold()
                if key in targets:
                    raise ValueError(f"Repeated export target: {target}")
                targets.add(key)
                if hashlib.sha256(content).hexdigest() != checksum:
                    raise ValueError(f"Source changed: {target}")
                path = root.joinpath(*relative.parts)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
                files.append({"path": str(relative), "sha256": checksum, "bytes": len(content)})
            if delivery.get("payload") is not None:
                write_checked("payload.txt", delivery["payload"].encode("utf-8"), delivery["payload_sha256"])
            for file in delivery.get("files", []):
                write_checked("source/" + file["path"], file["content"].encode("utf-8"), file["sha256"])
            for asset in delivery.get("assets", []):
                write_checked("source/" + asset["path"], Path(asset["original_path"]).read_bytes(), asset["sha256"])
            # Visual media are reference-only unless the caller has independent reuse rights.
            missing_media = []
            for asset in entry.get("record", {}).get("media", []):
                target = None
                try:
                    original = verified_media_path(asset)
                    target = root / "reference" / safe_relative(asset["path"])
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(original, target)
                    if sha256_file(target) != asset["sha256"]:
                        raise ValueError("Media changed during copy")
                    files.append({"path": target.relative_to(root).as_posix(), "sha256": asset["sha256"],
                                  "bytes": target.stat().st_size, "role": "reference_only"})
                except (OSError, ValueError) as exc:
                    missing_media.append({"path": asset["path"], "reason": str(exc)})
                    if target is not None and target.is_relative_to(root) and target.is_file():
                        target.unlink()
            records.append({"id": reference, "source": entry["source"], "url": entry["url"],
                            "retrieval": entry.get("retrieval"), "score": entry.get("score"),
                            "tier": delivery["tier"], "license": delivery.get("license"),
                            "dependencies": entry.get("material", {}).get("npm_deps"),
                            "source_bundle": delivery.get("source_bundle"),
                            "reference_contract": entry.get("reference_contract"),
                            "files": files, "missing_media": missing_media})
        manifest = {"version": 1, "query": packet.get("query", packet.get("brief")),
                    "backends": packet.get("backends"), "records": records,
                    "complete_build_verified": False}
        (staging / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        staging.rename(destination)
    return {"path": str(destination), "records": len(records), "manifest": str(destination / "manifest.json")}
