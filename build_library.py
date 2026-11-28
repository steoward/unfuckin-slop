"""Browse the installed model's corpus and select source material for a build."""
import argparse
from itertools import zip_longest
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
from uuid import uuid4

import search_design_showcases as search
from source_material import material_contract, full_evidence
from delivery_packet import export_packet
from semantic_index import DATA_DIR


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


def reference_contract(result):
    """Report the inputs required before claiming reference fidelity."""
    delivery = result["delivery"]
    inspection = result["inspection"]
    urls = {
        "source": result["url"],
        "video": result["video_url"],
        "registry": result["use"].get("registry_url"),
        "bundle": delivery.get("source_bundle", {}).get("source_url"),
    }
    exact_urls = {}
    for role, url in urls.items():
        if not url:
            continue
        try:
            parsed = urlsplit(url)
            if parsed.scheme in {"http", "https"} and parsed.hostname:
                exact_urls[role] = url
        except ValueError:
            continue
    missing = []
    if not result["id"]:
        missing.append("reference_id")
    if "source" not in exact_urls and "bundle" not in exact_urls:
        missing.append("original_source_url")
    if not delivery["payload"] and not delivery["files"]:
        missing.append("full_payload")
    if delivery["tier"] == "source_bundle" and delivery.get("bundle_status") != "verified":
        missing.append("verified_source_bundle")
    if delivery["tier"] == "registry_pointer":
        missing.append("verified_registry_source")
    if inspection["status"] != "verified":
        missing.append("verified_original_visual_evidence")
    return {
        "reference_id": result["id"],
        "urls": exact_urls,
        "visual_evidence_status": inspection["status"],
        "status": "missing_evidence" if missing else "comparison_required",
        "missing_evidence": missing,
        "comparison_required": True,
    }


def entry(row, pool, *, full=False):
    result = search.pack_reference(row)
    kind = result["material"]["kind"]
    action, instruction = ACTIONS.get(kind, ACTIONS["description"])
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
    result["delivery"] = material_contract(row, kind, full=full)
    if result["delivery"]["tier"] == "source_bundle":
        result["use"] = {"action": "integrate_bundle", "instruction": "Use the verified original files and assets, preserving dependencies, source revision and declared usage rights. Do not use an unavailable bundle."}
    if "relevance_score" in row:
        result["score"] = row["relevance_score"]
    if "retrieval" in row:
        result["retrieval"] = row["retrieval"]
    if full:
        result["record"] = {key: value for key, value in row.items() if key not in {"relevance_score", "visual_evidence", "retrieval"}}
        result["inspection"] = full_evidence(row, result["visual_evidence"])
        result["reference_contract"] = reference_contract(result)
    return result


def select(query, pool, records, candidates, limit, *, context=None, query_vector=None, visual_only=False):
    exact = [] if visual_only else search.exact_references(query, candidates)
    if exact:
        return [{**row, "retrieval": {"backend": "catalog_exact", "query": query}} for row in exact[:limit]], "catalog_exact"
    if query.startswith(("http://", "https://")):
        return [], "catalog_exact"
    ranking_query = context or query
    load_index = search._load_semantic_components if pool == "components" else search._load_semantic
    details = {}
    matches = search.rank_catalog(
        ranking_query, limit, records, load_index, components=pool == "components",
        candidate_ids={row["id"] for row in candidates}, diagnostics=details,
        query_vector=query_vector, allow_broad=True, visual_only=visual_only,
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
                exact_results.extend((row, pool) for row in candidates)
                continue
        results.append([(row, pool) for row in candidates])

    if exact_results:
        total = len(exact_results)
        page = [entry(row, pool, full=args.full) for row, pool in exact_results[args.offset:args.offset + args.limit]]
    else:
        if query or args.reference:
            # Pool scores are normalized independently. Interleave by rank.
            order = interleave(results)
        else:
            order = [item for batch in results for item in batch]
        total = len(order)
        page = [entry(row, pool, full=args.full) for row, pool in order[args.offset:args.offset + args.limit]]
    next_offset = args.offset + len(page)
    return {
        "status": "ok" if total else "no_matches",
        "total": total, "offset": args.offset,
        "next_offset": next_offset if next_offset < total else None,
        "backends": provenance, "items": page,
        "query": query,
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
    designs = [row for row in catalogs["designs"] if row.get("full_prompt") or row.get("media") or row.get("source_bundle")]
    components = catalogs["components"]
    if args.local:
        designs = [row for row in designs if row.get("full_prompt") or row.get("source_bundle")]
        components = [row for row in components if row.get("source_bundle") or (row["source_site"] == "skiper-ui.com" and row.get("full_prompt"))]
    foundation = [row for row in designs if row.get("type") in
                  {"hero", "landing", "landing-page", "3d website", "dashboard", "mobile", "showcase"}]
    # Do not assemble a generic five-section landing page around every brief.
    # The retrieved blueprint owns composition; supplementary slots are explicit.
    sections = args.section or [("hero", DEFAULT_SECTIONS["hero"])]
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
            "selected": entry(first, pool, full=True),
            "alternatives": [entry(row, pool, full=args.full) for row, pool in options[1:args.limit]],
        }

    pinned = search.exact_references(brief, designs)
    anchors, backend = select(brief, "designs", catalogs["designs"], pinned or foundation, args.limit,
                              query_vector=vectors.get(brief))
    blueprint = choose("page-blueprint", [(row, "designs") for row in anchors], {"designs": backend})
    parts = []
    for (name, query), context in zip(sections, queries[1:]):
        if not args.section and name == "hero" and anchors:
            selected = blueprint["selected"]
            parts.append({
                "name": name, "backends": blueprint["backends"],
                "selected": {key: value for key, value in selected.items()
                             if key not in {"record", "delivery", "inspection", "reference_contract"}},
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
        # Prefer an exact selection; otherwise choose page-level material for the hero,
        # and reusable components for discrete sections. Alternatives keep both pools.
        priority = sorted(options, key=lambda pool: (backends[pool] != "catalog_exact",
                          pool != ("designs" if name.casefold() == "hero" else "components")))
        ordered = interleave([[(row, pool) for row in options[pool]] for pool in priority])
        # Keep explicit IDs authoritative. For free-form requests prefer available
        # implementation within the retrieved candidates, not an unresolved pointer.
        if not any(backends[p] == "catalog_exact" for p in backends) and name.casefold() != "hero":
            original = [(row, pool) for row, pool in ordered
                        if row.get("source_bundle") or (row.get("source_site") == "skiper-ui.com" and row.get("full_prompt"))]
            if original:
                first = original[0]
                ordered = [first] + [item for item in ordered if item[0]["id"] != first[0]["id"]]
        parts.append(choose(name, ordered, backends))
    selected_slots = [blueprint, *parts]
    selected = [part["selected"] for part in selected_slots if part.get("selected") and not part.get("uses_blueprint")]
    gaps = [{"id": row["id"], "missing": row["reference_contract"]["missing_evidence"]}
            for row in selected if row["reference_contract"]["missing_evidence"]]
    lexical = [row["id"] for row in selected if row.get("retrieval", {}).get("backend") == "lexical"]
    return {
        "status": "ok" if blueprint["selected"] and all(p["selected"] for p in parts) else "partial",
        "brief": brief,
        "blueprint": blueprint, "sections": parts,
        "composition": {"policy": "single_blueprint", "mode": "pinned_reference" if pinned else "adaptation",
                        "anchor_id": blueprint["selected"]["id"] if blueprint["selected"] else None,
                        "supplementary_sections": [name for name, _ in args.section or []],
                        "rule": "Keep the blueprint's complete composition. Add only explicitly requested compatible sections; do not invent generic sections."},
        "execution_readiness": {"status": "review_required" if gaps or lexical or not selected else "comparison_required",
                                "evidence_gaps": gaps, "lexical_selections": lexical,
                                "quality_verified": False},
        "instructions": [
            "Choose reproduction for an unchanged reference or adaptation when the brief changes its content, assets or design. Pin the reference ID and keep its exact source and asset evidence.",
            "Read the full delivery payload and files. Open the original visual evidence and record the observed composition, type, assets and motion. A section marked uses_blueprint shares the blueprint's evidence and contract.",
            "Resolve every missing_evidence item for reproduction. Open an alternative by ID only when the selection is flexible. Report any unresolved evidence and avoid generic substitutions.",
            "For reproduction, preserve original assets, copy, layout and behavior where authorized. Only use suggested sections that match the pinned reference. For adaptation, implement the brief's changes and preserve the reference's observable design decisions.",
            "Render at matching viewports and interaction states, compare to verified original images or video frames, and report the source IDs, exact URLs, evidence, discrepancies and any unverified states.",
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
    parser.add_argument("--export-dir", type=Path, help="Export selected full material to a new private directory")
    parser.add_argument("--no-export", action="store_true", help="Inspect a plan without writing its private material packet")
    parser.add_argument("query", nargs="*")
    args = parser.parse_intermixed_args()
    if args.no_export and (args.export_dir or args.operation != "plan"):
        parser.error("--no-export is for plan and conflicts with --export-dir")
    if args.export_dir and args.operation == "library":
        args.full = True
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
    elif args.section or args.local:
        parser.error("--section and --local are for plan")
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
    if args.operation == "plan" and not args.no_export and not args.export_dir and result["blueprint"]["selected"]:
        root = Path(os.environ.get("UNFSLOP_DELIVERY_ROOT", DATA_DIR / ".deliveries"))
        args.export_dir = root / uuid4().hex
    if args.export_dir:
        try:
            result["export"] = export_packet(result, args.export_dir)
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
