#!/usr/bin/env python3
"""Search the local design and component catalogs.

MiniLM and lexical search rank text. Evidence packets identify the original
record and what the snapshot contains. Use --record for the stored payload.
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from collections import Counter
from functools import cache
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.metrics.pairwise import cosine_similarity

SHOWCASES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "design_showcases")
META_PATH = os.path.join(SHOWCASES_DIR, "showcases_meta.json")
EMBS_PATH = os.path.join(SHOWCASES_DIR, "design_embeddings.npy")
# Separate UI-component pool (21st.dev + skiper.ui code prompts). Kept apart from the
# 950 full-design showcases so the design benchmark and design search stay clean.
COMPONENTS_META_PATH = os.path.join(SHOWCASES_DIR, "components_meta.json")
COMPONENTS_EMBS_PATH = os.path.join(SHOWCASES_DIR, "component_embeddings.npy")

# The semantic layer is optional. Both pools use the same encoder.
SEMANTIC_WEIGHT = 0.7


@cache
def _encoder():
    from semantic_index import load_encoder

    return load_encoder()


@cache
def _load_index(path):
    encoder = _encoder()
    if encoder is not None:
        try:
            return encoder, np.load(path)
        except (OSError, ValueError):
            pass
    return None, None


def _load_semantic():
    return _load_index(EMBS_PATH)


def _load_semantic_components():
    return _load_index(COMPONENTS_EMBS_PATH)


def _minmax(x):
    lo, hi = float(np.min(x)), float(np.max(x))
    return (x - lo) / max(hi - lo, 1e-9)

# 3D, WebGL, and Kinetic keywords for filtering and classification
THREED_KEYWORDS = [
    "3d", "webgl", "canvas", "particle", "liquid", "kinetic", "spatial",
    "camera", "mesh", "tilt", "refraction", "orbit", "shader", "glsl",
    "perspective", "physics", "point-cloud", "cyber", "neon", "bento", "glass",
    "three.js", "threejs", "spline", "r3f"
]

# Liquid Glass, Refraction, and Chromatic aberration keywords
LIQUID_GLASS_KEYWORDS = [
    "liquid", "glass", "refraction", "refractive", "chromatic", "aberration",
    "glassmorphism", "frosted glass", "lens distortion", "specular", "caustics", "prism",
    "liquid glass"
]

def get_item_category(item) -> str:
    """Return explicit category or infer one intelligently."""
    cat = item.get("category")
    if cat and str(cat).strip():
        return str(cat).strip()

    text = f"{item.get('title', '')} {item.get('description', '')}".lower()
    if any(k in text for k in ["liquid", "refraction", "glass", "chromatic"]):
        return "Liquid Glass"
    if any(k in text for k in ["3d", "webgl", "canvas", "particle", "mesh", "orbit", "shader", "point-cloud"]):
        return "3D & Spatial"
    if any(k in text for k in ["crypto", "trading", "fintech", "wallet", "finance", "bank"]):
        return "Fintech"
    if any(k in text for k in ["ai", "agent", "bot", "assistant", "model", "prompt"]):
        return "AI & Machine Learning"
    if any(k in text for k in ["saas", "dashboard", "analytics", "metric", "b2b"]):
        return "SaaS & Dashboard"
    if any(k in text for k in ["fashion", "luxury", "apparel", "wear", "editorial"]):
        return "Fashion"
    if any(k in text for k in ["ecommerce", "shop", "store", "product", "checkout", "cart"]):
        return "Ecommerce"
    if any(k in text for k in ["hero", "headline", "landing"]):
        return "Hero & Landing"
    if any(k in text for k in ["portfolio", "agency", "creator", "studio"]):
        return "Portfolio & Agency"
    if any(k in text for k in ["developer", "code", "terminal", "ide", "api", "replay"]):
        return "Developer Tools"
    return "UI Motion Showcase"

def get_source_info(item):
    """Extract source website and URL cleanly."""
    source_site = item.get("source_site")
    source_url = item.get("source_url") or ""
    if not source_site:
        if "motionsites.ai" in source_url:
            source_site = "motionsites.ai"
        elif "pixlpin.com" in source_url:
            source_site = "pixlpin.com"
        else:
            source_site = "Curated UI Showcase"
    return source_site, source_url

def is_liquid_glass_showcase(item) -> bool:
    """Check if showcase exhibits liquid glass, glassmorphism, or refractive dynamics."""
    if item.get("is_liquid_glass") is True:
        return True
    text = f"{item.get('title', '')} {item.get('description', '')} {item.get('category', '')} {item.get('id', '')} {str(item.get('full_prompt', ''))[:400]}".lower()
    return any(k in text for k in LIQUID_GLASS_KEYWORDS)

def is_3d_showcase(item) -> bool:
    """Check if showcase exhibits 3D, WebGL, particle, kinetic, or spatial dynamics."""
    if item.get("is_3d") is True:
        return True
    text = f"{item.get('title', '')} {item.get('description', '')} {item.get('category', '')} {item.get('id', '')} {str(item.get('full_prompt', ''))[:400]}".lower()
    return any(k in text for k in THREED_KEYWORDS)

def matches_category(item, category_query: str) -> bool:
    """Case-insensitive substring or exact match on category."""
    if not category_query:
        return True
    cat = get_item_category(item).lower()
    cq = category_query.strip().lower()
    return cq in cat or cq == cat

# Words that carry no specific design subject on their own. A query made up
# entirely of these (plus English stopwords) is genuinely vague and falls back
# to the archetype defaults; any real subject word makes it a retrieval query.
_GENERIC_QUERY_WORDS = frozenset({
    "creative", "creativity", "landing", "hero", "showcase", "portfolio",
    "homepage", "website", "web", "site", "page", "app", "application",
    "ui", "ux", "design", "build", "modern", "cool", "best", "great",
    "awesome", "nice", "beautiful", "stunning", "something", "anything",
    "archetype", "archetypes", "brief", "project", "new", "mind", "blowing",
    "director", "system", "components", "component", "explore", "exploration",
    "inspiration", "ideas", "idea", "concept", "demo", "choice", "choose",
    "pick", "select", "example", "examples", "sample", "samples", "random",
    "whatever", "stuff", "things", "thing", "kind", "sort", "type", "types",
    "style", "styles", "look", "feel", "vibe", "vibes", "aesthetic",
})


def is_broad_or_creative_query(query: str) -> bool:
    """True only for empty or genuinely subject-free queries.

    A specific product/service brief (e.g. 'space travel brand landing page
    selling seats to mars') must retrieve real showcases, not archetype
    defaults. Strip English stopwords and generic web/design filler; if any
    substantive subject word remains, the query is specific and gets retrieved.
    """
    q = query.strip().lower()
    if not q:
        return True
    words = [w for w in re.split(r"[^a-z0-9]+", q) if len(w) > 1]
    content = [w for w in words
               if w not in ENGLISH_STOP_WORDS and w not in _GENERIC_QUERY_WORDS]
    return len(content) == 0

def list_categories(items):
    """Print all available categories with their item counts and exit."""
    counts = Counter()
    for it in items:
        cat = get_item_category(it)
        counts[cat] += 1

    total_items = len(items)
    print("\n=======================================================")
    print(f" UI Design System & Component Library Categories ({total_items} items total)")
    print("=======================================================\n")
    for cat, count in counts.most_common():
        pct = (count / total_items) * 100 if total_items else 0
        bar = "█" * max(1, int(pct / 2.5))
        print(f"  • {cat:<26} {count:>4} items ({pct:>4.1f}%)  {bar}")
    print(f"\nTotal: {len(counts)} categories across {total_items} showcases.\n")

def load_catalog(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []


def load_data():
    return load_catalog(META_PATH)


def load_components():
    return load_catalog(COMPONENTS_META_PATH)


def matches_filters(item, source, category, only_3d, only_glass):
    return ((not source or get_source_info(item)[0] == source)
            and (not category or matches_category(item, category))
            and (not only_3d or is_3d_showcase(item))
            and (not only_glass or is_liquid_glass_showcase(item)))


def rank_catalog(query, limit, records, load_semantic, *, components=False,
                 filter_3d=False, filter_liquid_glass=False, category_filter=None,
                 source_filter=None, diagnostics=None, candidate_ids=None, query_vector=None,
                 allow_broad=False):
    """Keep original row positions for vector lookup when filtering."""
    indexed = [(i, item) for i, item in enumerate(records)
               if (candidate_ids is None or item["id"] in candidate_ids)
               and matches_filters(item, source_filter, category_filter,
                                   filter_3d, filter_liquid_glass)]
    if diagnostics is not None:
        diagnostics["catalog_available"] = bool(records)
    if not indexed:
        return []

    items = [item for _, item in indexed]
    limit = 5 if limit is None else limit
    if not allow_broad and is_broad_or_creative_query(query):
        if not (source_filter or category_filter or filter_3d or filter_liquid_glass or components):
            return []
        return [{**item, "relevance_score": 1.0} for item in items[:limit]]

    titles = [item.get("title", "") for item in items]
    categories = [get_item_category(item) for item in items]
    descriptions = [item.get("description", "") for item in items]
    tags = [" ".join(item.get("tags", [])) if components else "" for item in items]
    corpus = [
        f"{title} {title} {category} {desc} {item.get('id', '').replace('-', ' ')} {tag}"
        for item, title, category, desc, tag in zip(items, titles, categories, descriptions, tags)
    ]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    try:
        matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        similarities = np.zeros(len(items))
    else:
        similarities = cosine_similarity(vectorizer.transform([query]), matrix).ravel()

    lower_query = query.lower()
    terms = [word for word in lower_query.split() if len(word) > 2]
    wants_3d = filter_3d or any(word in lower_query for word in THREED_KEYWORDS)
    wants_glass = filter_liquid_glass or any(word in lower_query for word in LIQUID_GLASS_KEYWORDS)
    spatial_words = ("3d", "webgl", "particle", "liquid", "kinetic", "canvas")
    glass_words = ("liquid", "glass", "refraction", "chromatic", "frosted")
    scores = []
    for similarity, title, category, desc, tag in zip(similarities, titles, categories, descriptions, tags):
        title, category, desc, tag = title.lower(), category.lower(), desc.lower(), tag.lower()
        boost = sum(0.35 for word in terms if word in title)
        boost += sum(0.20 for word in terms if word in category)
        boost += sum(0.15 for word in terms if word in desc)
        boost += sum(0.10 for word in terms if word in tag)
        if wants_3d:
            if any(word in title for word in spatial_words):
                boost += 0.35
            elif any(word in desc for word in spatial_words):
                boost += 0.15
        if wants_glass:
            if any(word in title for word in glass_words):
                boost += 0.40
            elif any(word in desc for word in glass_words):
                boost += 0.20
        scores.append(float(similarity) + boost)

    scores = np.asarray(scores)
    encoder, embeddings = load_semantic()
    hybrid = encoder is not None and embeddings is not None and embeddings.shape[0] == len(records)
    if hybrid:
        vector = encoder.encode([query])[0] if query_vector is None else query_vector
        semantic = embeddings[[i for i, _ in indexed]] @ vector
        scores = (1.0 - SEMANTIC_WEIGHT) * _minmax(scores) + SEMANTIC_WEIGHT * _minmax(semantic)
    if diagnostics is not None:
        diagnostics["backend"] = "hybrid" if hybrid else "lexical"

    ranked = sorted(zip(scores, items), key=lambda pair: pair[0], reverse=True)
    return [{**item, "relevance_score": round(float(score), 4)}
            for score, item in ranked[:limit] if score > 0.05 or not terms]


def search(query="", limit=None, filter_3d=False, filter_liquid_glass=False,
           category_filter=None, *, records=None, **filters):
    return rank_catalog(query, limit, load_data() if records is None else records,
                        _load_semantic, filter_3d=filter_3d, filter_liquid_glass=filter_liquid_glass,
                        category_filter=category_filter, **filters)


def search_components(query="", limit=None, filter_3d=False, filter_liquid_glass=False,
                      category_filter=None, *, records=None, **filters):
    return rank_catalog(query, limit, load_components() if records is None else records,
                        _load_semantic_components, components=True, filter_3d=filter_3d,
                        filter_liquid_glass=filter_liquid_glass, category_filter=category_filter, **filters)


REFERENCE_SOURCES = {
    "designs": ("motionsites.ai", "pixlpin.com"),
    "components": ("skiper-ui.com", "21st.dev"),
}

SOURCE_MATERIAL = {
    "motionsites.ai": "design_prompt",
    "pixlpin.com": "description",
    "skiper-ui.com": "component_source_snapshot",
    "21st.dev": "registry_instructions",
}


def pack_reference(item):
    source, url = get_source_info(item)
    body = (item.get("full_prompt") or "").strip()
    material = {
        "kind": SOURCE_MATERIAL.get(source, "catalog_text") if body else "description",
        "characters": len(body),
        "excerpt_truncated": len(body) > 550,
    }
    for key in ("author", "license", "npm_deps"):
        if item.get(key):
            material[key] = item[key]
    return {
        "id": item.get("id"), "title": item["title"], "source": source,
        "url": url or None, "video_url": item.get("video_url") or None,
        "description": (item.get("description") or "")[:750],
        "blueprint_excerpt": body[:550] or None,
        "material": material,
    }


def exact_references(query, rows):
    """Try a canonical ID or source URL before matching titles."""
    key = query.strip()
    if not key:
        return []
    identified = [row for row in rows
                  if row.get("id") == key or get_source_info(row)[1].rstrip("/") == key.rstrip("/")]
    if identified:
        return identified
    title = " ".join(key.casefold().split())
    return [row for row in rows if " ".join(row["title"].casefold().split()) == title]


def reference_evidence(query, pool, *, limit=3, filter_3d=False,
                       filter_liquid_glass=False, category_filter=None, source_filter=None):
    """Return catalog evidence. Preserve the existing hybrid ranking for briefs."""
    if source_filter and source_filter not in REFERENCE_SOURCES[pool]:
        return {"status": "invalid_source", "backend": None, "references": [],
                "reason": f"Choose a {pool} source: {', '.join(REFERENCE_SOURCES[pool])}."}
    constrained = filter_3d or filter_liquid_glass or category_filter or source_filter
    broad = is_broad_or_creative_query(query)
    records = load_components() if pool == "components" else load_data()
    if not records:
        return {"status": "unavailable", "backend": None, "references": [],
                "reason": f"The {pool} catalog could not be loaded."}
    candidates = [row for row in records
                  if matches_filters(row, source_filter, category_filter,
                                     filter_3d, filter_liquid_glass)]
    exact = exact_references(query, candidates)
    if len(exact) == 1:
        return {"status": "ok" if limit else "no_matches", "backend": "catalog_exact",
                "exact_matches": len(exact), "references": [pack_reference(row) for row in exact[:limit]]}

    key = query.strip()
    if not exact and (key.startswith(("https://", "http://"))
                      or any(row.get("id") == key for row in records)):
        return {"status": "no_matches", "backend": "catalog_exact", "exact_matches": 0, "references": []}
    if broad and not constrained and not exact:
        return {"status": "needs_specific_query", "backend": None, "references": []}

    details = {"backend": "catalog_filter" if broad else None}
    # Preserve the existing ranking when multiple records share an exact title.
    rank_limit = len(records) if exact else limit
    options = dict(limit=rank_limit, filter_3d=filter_3d, filter_liquid_glass=filter_liquid_glass,
                   category_filter=category_filter, source_filter=source_filter, diagnostics=details, records=records)
    if pool == "components":
        matches = search_components(query, **options)
    else:
        matches = search(query, **options)
    if exact:
        rank = {row["id"]: i for i, row in enumerate(matches)}
        exact.sort(key=lambda row: rank.get(row["id"], len(rank)))
        return {"status": "ok" if limit else "no_matches", "backend": "catalog_exact",
                "exact_matches": len(exact), "references": [pack_reference(row) for row in exact[:limit]]}
    return {"status": "ok" if matches else "no_matches", "backend": details["backend"],
            "references": [pack_reference(row) for row in matches]}


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Search the local UI reference catalog")
    parser.add_argument("query", nargs="*")
    parser.add_argument("--pool", choices=REFERENCE_SOURCES, default="designs")
    parser.add_argument("--3d", dest="three_d", action="store_true")
    parser.add_argument("--liquid-glass", action="store_true")
    parser.add_argument("--category")
    parser.add_argument("--full", action="store_true", help="Print the stored reference text")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--json", action="store_true")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--list-categories", action="store_true")
    mode.add_argument("--evidence", action="store_true", help="Return compact source evidence as JSON")
    parser.add_argument("--source", choices=sorted(SOURCE_MATERIAL))
    mode.add_argument("--record", metavar="ID", help="Print one original catalog record as JSON")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 0:
        parser.error("--limit must be nonnegative")
    if args.source and args.source not in REFERENCE_SOURCES[args.pool]:
        parser.error(f"--source {args.source} is outside the {args.pool} pool")

    load = load_components if args.pool == "components" else load_data
    if args.record or args.list_categories:
        matches = [row for row in load() if matches_filters(
            row, args.source, args.category, args.three_d, args.liquid_glass)]
    if args.record:
        record = next((row for row in matches if row.get("id") == args.record), None)
        if record is None:
            parser.error(f"unknown {args.pool} record {args.record!r}")
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return
    if args.list_categories:
        list_categories(matches)
        return

    query = " ".join(args.query)
    filters = dict(filter_3d=args.three_d, filter_liquid_glass=args.liquid_glass,
                   category_filter=args.category, source_filter=args.source)
    if args.evidence:
        result = reference_evidence(query, args.pool, limit=3 if args.limit is None else args.limit,
                                    **filters)
        print(json.dumps(result, ensure_ascii=False))
        return

    search_pool = search_components if args.pool == "components" else search
    results = search_pool(query, limit=args.limit, **filters)
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
    for record in results:
        _, url = get_source_info(record)
        print(f"{record['title']} [{record['id']}] ({record['relevance_score']})")
        if url:
            print(url)
        print(record.get("description", ""))
        if args.full and record.get("full_prompt"):
            print(record["full_prompt"])
        print()
    if not results:
        print("No references. Try a specific design query or select a source.")


if __name__ == "__main__":
    main()
