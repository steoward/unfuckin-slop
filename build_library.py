"""Browse the installed model's corpus and select source material for a build."""
import argparse
from itertools import zip_longest
import json
from pathlib import Path
import re
import sys

import search_design_showcases as search


DEFAULT_SECTIONS = {
    "navigation": "responsive brand navigation with mobile menu",
    "hero": "product headline, product preview and primary action",
    "features": "product benefits and feature grid with descriptive cards",
    "call-to-action": "closing call to action with one primary button",
    "footer": "site footer with product links and brand information",
}

# Use role metadata to keep decorative or unrelated components out of generic slots.
ROLE_PATTERN = {
    "navigation": r"\b(navbar|navigation|site header|mobile menu)\b",
    "hero": r"\bhero\b",
    "features": r"\b(features?|feature grid|bento grid)\b",
    "call-to-action": r"\b(cta|call[ -]to[ -]action)\b",
    "footer": r"\bfooter\b",
    "pricing": r"\bpricing\b",
    "faq": r"\b(faq|accordion)\b",
    "testimonials": r"\b(testimonial[s]?|reviews)\b",
}

REGISTRY_URL = re.compile(
    r'^Install: npx shadcn@latest add "(https://21st\.dev/r/(?:[\w.-]|%[0-9A-Fa-f]{2})+/[\w.-]+)'
    r'\?api_key=\$API_KEY_21ST"$', re.MULTILINE | re.ASCII,
)

ACTIONS = {
    "design_prompt": ("adapt_prompt", "Apply the stored layout and interaction to the product's copy, assets and stack."),
    "component_source_snapshot": ("adapt_source", "Integrate the stored source and resolve its imports, assets and dependencies in the project."),
    "registry_instructions": ("implement_from_description", "Check the source for usable code or implement the described pattern in the project."),
    "description": ("adapt_pattern", "Use the stored description and available preview to implement the pattern for the product."),
}


def entry(row, pool, *, full=False):
    result = search.pack_reference(row)
    kind = result["material"]["kind"]
    action, instruction = ACTIONS[kind]
    use = {"action": action, "instruction": instruction}
    if kind == "registry_instructions":
        match = REGISTRY_URL.search(row["full_prompt"])
        if match:
            use = {
                "action": "install_registry",
                "instruction": "Review the registry item and install it in a compatible shadcn project. Otherwise implement its stored description.",
                "registry_url": match[1],
                "installer": ["npx", "shadcn@latest", "add"],
                "credential_env": "API_KEY_21ST",
                "credential_parameter": "api_key",
            }
    result.update(pool=pool, category=search.get_item_category(row), type=row.get("type"), use=use)
    if "relevance_score" in row:
        result["score"] = row["relevance_score"]
    if full:
        result["record"] = {key: value for key, value in row.items() if key not in {"relevance_score", "visual_evidence"}}
    return result


def select(query, pool, records, candidates, limit, *, context=None, query_vector=None, visual_only=False):
    exact = [] if visual_only else search.exact_references(query, candidates)
    if exact:
        return exact[:limit], "catalog_exact"
    if query.startswith(("http://", "https://")):
        return [], "catalog_exact"
    ranking_query = context or query
    load_index = search._load_semantic_components if pool == "components" else search._load_semantic
    details = {}
    matches = search.rank_catalog(
        ranking_query, limit, records, load_index, components=pool == "components",
        candidate_ids={row["id"] for row in candidates}, diagnostics=details,
        query_vector=query_vector, allow_broad=True,
    )
    return matches, details.get("backend")


def interleave(groups):
    return [item for batch in zip_longest(*groups) for item in batch if item]


def browse(args, catalogs, query):
    results, provenance = [], {}
    vector = None
    exact_results = []
    for pool, rows in catalogs.items():
        candidates = [row for row in rows if search.matches_filters(
            row, args.source, args.category, False, False)]
        if args.reference:
            index = search.open_index("components" if pool == "components" else "showcases")
            if index is None or not index.visual.size:
                provenance[pool] = "no_visual_index"
                continue
            candidates = [item for item in candidates if item.get("media")]
            if vector is None and candidates:
                vector = search.query_vectors([query], args.reference)[0]
        if query or args.reference:
            candidates, backend = select(query, pool, rows, candidates, len(rows), query_vector=vector,
                                         visual_only=bool(args.reference))
            provenance[pool] = backend
            if backend == "catalog_exact":
                exact_results.extend(entry(row, pool) for row in candidates)
                continue
        results.append([(row, pool) for row in candidates])

    if exact_results:
        total = len(exact_results)
        page = exact_results[args.offset:args.offset + args.limit]
    else:
        if query or args.reference:
            # Pool scores are normalized independently. Interleave by rank.
            order = interleave(results)
        else:
            order = [item for batch in results for item in batch]
        total = len(order)
        page = [entry(row, pool) for row, pool in order[args.offset:args.offset + args.limit]]
    next_offset = args.offset + len(page)
    return {
        "status": "ok" if total else "no_matches",
        "total": total, "offset": args.offset,
        "next_offset": next_offset if next_offset < total else None,
        "backends": provenance, "items": page,
    }


def section_spec(text):
    name, separator, query = text.partition("=")
    if not separator or not name.strip() or not query.strip():
        raise argparse.ArgumentTypeError("use --section NAME=QUERY")
    return name.strip(), query.strip()


def matches_role(row, pattern):
    fields = (row["title"], search.get_item_category(row), row.get("type", ""))
    return any(re.search(pattern, field, re.IGNORECASE) for field in fields)


def build_plan(args, catalogs, brief):
    designs = [row for row in catalogs["designs"] if row.get("full_prompt") or row.get("media")]
    components = catalogs["components"]
    if args.local:
        components = [row for row in components if row["source_site"] == "skiper-ui.com"]
    foundation = [row for row in designs if row.get("type") in
                  {"hero", "landing", "landing-page", "3d website", "dashboard", "mobile", "showcase"}]
    sections = args.section or list(DEFAULT_SECTIONS.items())
    queries = [brief, *(f"{query} for {brief}" for _, query in sections)]
    indexed = search.open_index("showcases") is not None or search.open_index("components") is not None
    vectors = dict(zip(queries, search.query_vectors(queries))) if indexed else {}
    selected_ids = set()

    def choose(name, options, backends):
        if not options:
            return {"name": name, "backends": backends, "selected": None, "alternatives": []}
        first, pool = options[0]
        selected_ids.add(first["id"])
        return {
            "name": name,
            "backends": backends,
            "selected": entry(first, pool, full=args.full),
            "alternatives": [entry(row, pool) for row, pool in options[1:args.limit]],
        }

    anchors, backend = select(brief, "designs", catalogs["designs"], foundation, args.limit,
                              query_vector=vectors.get(brief))
    blueprint = choose("page-blueprint", [(row, "designs") for row in anchors], {"designs": backend})
    parts = []
    for (name, query), context in zip(sections, queries[1:]):
        if not args.section and name == "hero" and anchors and anchors[0]["type"] == "hero":
            selected = blueprint["selected"]
            parts.append({
                "name": name, "backends": blueprint["backends"],
                "selected": {key: value for key, value in selected.items() if key != "record"},
                "alternatives": [], "uses_blueprint": True,
            })
            continue

        pattern = ROLE_PATTERN.get(name.casefold())
        options, backends = {}, {}
        for pool, rows in (("components", components), ("designs", designs)):
            available = [row for row in rows if row["id"] not in selected_ids]
            exact = search.exact_references(query, rows)
            if exact:
                candidates = exact
            elif pattern:
                candidates = [row for row in available if matches_role(row, pattern)]
            else:
                candidates = available
            options[pool], backends[pool] = select(
                query, pool, catalogs[pool], candidates, args.limit,
                context=context, query_vector=vectors.get(context),
            )
        priority = sorted(options, key=lambda pool: backends[pool] != "catalog_exact")
        ordered = [[(row, pool) for row in options[pool]] for pool in priority]
        parts.append(choose(name, interleave(ordered), backends))
    return {
        "status": "ok" if blueprint["selected"] and all(p["selected"] for p in parts) else "partial",
        "brief": brief,
        "blueprint": blueprint, "sections": parts,
        "instructions": [
            "Open visual_evidence at its indicated timestamp when available. Record the observed hierarchy, composition and motion before implementing.",
            "Use the selected blueprint as the page's visual foundation. It may cover a single section.",
            "Build each section from its selected material. Use an alternative if it fits the stack or interaction better.",
            "Open all selected IDs together with unfslop library --record ID --record ID, or rerun with --full. A section marked uses_blueprint uses the same material.",
            "Use one set of tokens, real product copy and functional actions. For a missing selection, search the library for that section.",
        ],
    }


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("library", "plan"))
    parser.add_argument("--pool", choices=search.REFERENCE_SOURCES)
    parser.add_argument("--source", choices=search.SOURCE_MATERIAL)
    parser.add_argument("--category")
    parser.add_argument("--reference", type=Path, help="Local screenshot used for visual search")
    parser.add_argument("--record", action="append")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--section", action="append", type=section_spec)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--local", action="store_true")
    parser.add_argument("query", nargs="*")
    args = parser.parse_intermixed_args()
    query = " ".join(args.query).strip()
    if args.limit is None:
        args.limit = 3 if args.operation == "plan" else 20
    if args.offset < 0 or not 1 <= args.limit <= (10 if args.operation == "plan" else 100):
        parser.error("offset must be nonnegative and limit must be 1–10 for plan or 1–100 for library")
    if args.source and args.pool and args.source not in search.REFERENCE_SOURCES[args.pool]:
        parser.error("source must belong to the requested pool")

    catalogs = {}
    for pool, load in (("designs", search.load_data), ("components", search.load_components)):
        if (not args.pool or args.pool == pool) and (
                not args.source or args.source in search.REFERENCE_SOURCES[pool]):
            catalogs[pool] = load()
            if not catalogs[pool]:
                parser.error(f"the {pool} catalog could not be loaded")

    if args.operation == "plan":
        if not query or any((args.pool, args.source, args.category, args.record, args.offset, args.reference)):
            parser.error("plan requires a brief and accepts --section, --limit, --local and --full")
        if args.section and len({name.casefold() for name, _ in args.section}) != len(args.section):
            parser.error("section names must be unique")
        result = build_plan(args, catalogs, query)
    elif args.section or args.full or args.local:
        parser.error("--section, --full and --local are for plan")
    elif args.record:
        if query or args.source or args.category or args.offset or args.reference:
            parser.error("--record accepts IDs and an optional --pool")
        by_id = {row["id"]: (row, pool) for pool, rows in catalogs.items() for row in rows}
        missing = [record_id for record_id in args.record if record_id not in by_id]
        if missing:
            parser.error(f"unknown record IDs: {', '.join(missing)}")
        result = {"status": "ok", "items": [entry(*by_id[record_id], full=True) for record_id in args.record]}
    else:
        result = browse(args, catalogs, query)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
