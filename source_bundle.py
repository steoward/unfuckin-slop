"""Import and verify authorized, privately stored original implementation files."""
import hashlib
import json
from pathlib import Path, PurePosixPath


def safe_relative(value):
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise ValueError(f"Expected a portable relative path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or str(path) == ".":
        raise ValueError(f"Unsafe relative path: {value!r}")
    return path


def resolve_file(root, value):
    root = root.resolve()
    path = root.joinpath(*safe_relative(value).parts).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise FileNotFoundError(f"Missing source file inside source root: {value}")
    return path


def sha256_file(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def attach_source_bundles(manifest, root, rows):
    """A manifest declares the user's rights and immutable source revision.

    This verifies the supplied bytes and path boundaries, not legal permission.
    No registry calls, downloads or executable installation happen here.
    """
    seen = set()
    for line in manifest.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        record_id = item["id"]
        if record_id not in rows or record_id in seen:
            raise ValueError(f"Unknown or repeated source bundle ID: {record_id}")
        seen.add(record_id)
        _, row = rows[record_id]
        for key in ("revision", "license", "rights"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError(f"Source bundle {record_id} requires {key}")
        if item.get("source_url") != row["source_url"]:
            raise ValueError(f"Source URL differs from catalog for {record_id}")
        dependencies = item.get("dependencies", [])
        if not isinstance(dependencies, list) or not all(isinstance(x, str) and x.strip() for x in dependencies):
            raise ValueError(f"Invalid dependency list for {record_id}")
        files, targets = [], set()
        for asset in item.get("files", []):
            target = str(safe_relative(asset["target"]))
            path = resolve_file(root, asset["path"])
            kind = asset.get("kind", "text")
            if kind not in {"text", "asset"} or target.casefold() in targets:
                raise ValueError(f"Invalid or repeated source target: {target}")
            if kind == "text":
                path.read_bytes().decode("utf-8")
            targets.add(target.casefold())
            checksum = sha256_file(path)
            if asset.get("sha256", checksum) != checksum:
                raise ValueError(f"Source checksum mismatch: {asset['path']}")
            files.append({"path": str(safe_relative(asset["path"])), "target": target,
                          "kind": kind, "sha256": checksum})
        if not any(file["kind"] == "text" for file in files):
            raise ValueError(f"Source bundle {record_id} must contain original source text")
        row["source_bundle"] = {"source_url": row["source_url"], "revision": item["revision"],
                                "license": item["license"], "rights": item["rights"],
                                "dependencies": dependencies, "files": files}


def open_source_bundle(bundle, root):
    """Only return material when all declared files still match their digests."""
    files, assets = [], []
    for item in bundle["files"]:
        path = resolve_file(root, item["path"])
        target = str(safe_relative(item["target"]))
        if item["kind"] == "text":
            payload = path.read_bytes()
            checksum = hashlib.sha256(payload).hexdigest()
            files.append({"path": target, "content": payload.decode("utf-8"), "sha256": checksum})
        elif item["kind"] == "asset":
            checksum = sha256_file(path)
            assets.append({"path": target, "original_path": str(path), "sha256": checksum})
        else:
            raise ValueError(f"Invalid bundle file kind: {item['kind']}")
        if checksum != item["sha256"]:
            raise ValueError(f"Source checksum mismatch: {item['path']}")
    return files, assets
