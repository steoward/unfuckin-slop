"""Validate media captions and expose visual descriptions for retrieval."""
import math
from numbers import Real


def _short_text(value, field, limit):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > limit:
        raise ValueError(f"Invalid annotation {field}")
    return value.strip()


def validate_annotation(report, asset_sha256, record_id, duration):
    if report.get("asset_sha256") != asset_sha256 or report.get("catalog_id") != record_id:
        raise ValueError(f"Annotation identity or asset hash mismatch for {record_id}")
    source = report.get("annotation")
    if not isinstance(source, dict):
        raise ValueError("An annotation object is required")

    def list_of_text(name, limit):
        values = source.get(name)
        if not isinstance(values, list) or not 1 <= len(values) <= 12:
            raise ValueError(f"Invalid annotation {name}")
        return [_short_text(value, name, limit) for value in values]

    result = {
        "provider": _short_text(report.get("provider"), "provider", 80),
        "model": _short_text(report.get("model_display_name"), "model", 80),
        "summary": _short_text(source.get("summary"), "summary", 850),
        "composition": list_of_text("composition", 420),
        "palette": list_of_text("palette", 60),
        "observed_motion": _short_text(source.get("observed_motion"), "observed_motion", 1600),
        "moments": [],
    }
    moments = source.get("moments", [])
    if not isinstance(moments, list) or len(moments) > 120:
        raise ValueError("Invalid annotation moments")
    for moment in moments:
        seconds = moment.get("seconds") if isinstance(moment, dict) else None
        if (isinstance(seconds, bool) or not isinstance(seconds, Real) or not math.isfinite(seconds)
                or seconds < 0 or seconds > duration
                or (result["moments"] and seconds <= result["moments"][-1]["seconds"])):
            raise ValueError(f"Annotation timestamps must be increasing and within the clip: {record_id}")
        result["moments"].append({"seconds": seconds,
                                  "observation": _short_text(moment.get("observation"), "observation", 650)})
    return result


def annotation_text(row):
    descriptions = []
    for asset in row.get("media", []):
        if annotation := asset.get("annotation"):
            descriptions.extend((annotation["summary"], *annotation["composition"],
                                 ", ".join(annotation["palette"]), annotation["observed_motion"]))
            descriptions.extend(moment["observation"] for moment in annotation["moments"])
    return " ".join(descriptions)


def window_annotation(asset, start, end):
    annotation = asset.get("annotation")
    if not annotation:
        return None
    return {**annotation, "moments": [item for item in annotation["moments"]
                                     if start <= item["seconds"] < end]}
