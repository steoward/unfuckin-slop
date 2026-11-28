---
name: unfuckin-slop
description: "Build web interfaces from a private EmbeddingGemma 2 library of page prompts, UI components and visual references. Use when asked to build with unfuckin-slop or to search its catalog. Also supplies Apple Design and Impeccable guidance for UI refinement, interaction design and critique."
---

# Unfuckin-Slop

Start with the person using the screen. Identify their main action, what they need to see before acting, and what counts as success. In an existing app, inspect the component, its callers, nearby UI, and a rendered example when available.

## Choose the scope

| Request | First move | Deliverable |
| --- | --- | --- |
| New screen or redesign | Name the primary action and run the library build plan. | A working screen with real hierarchy and a usable primary flow. |
| Refine or repair | Reproduce the issue. Reuse existing tokens, components, copy and interaction contracts. | The smallest coherent change that solves the observed problem. |
| Review | Identify the route, screenshot or files under review and the evidence each provides. | Findings ordered by impact. Edit only when requested. |
| Motion or system work | Isolate the gesture, state transition, token or shared primitive and inspect a real consumer. | A change verified in context, including recovery or fallback where applicable. |

Treat the user's brief and established product conventions as design inputs. Preserve factual claims, supported languages and working actions. For an open brief, pick one concrete organizing idea. On an inventory screen that could mean grouping by stock status with the next action alongside each exception. Decorative effects need a purpose on that surface.

## Build from the model library

When asked to build a new site or screen with unfuckin-slop, use the library's selected material to build the page. For **reference reproduction**, pin the requested reference and preserve its copy, assets, layout, states and motion where authorized. For **adaptation**, name what the brief changes and preserve the reference's remaining design decisions. Use the same evidence and comparison workflow for both.

1. Run `unfslop plan "<product, primary action, interaction and layout constraints>"`. Use a concise English retrieval brief and keep the interface in the requested language. The blueprint governs the entire composition; do not wrap it in a stock landing-page template. Only request supplementary parts with repeated `--section "name=focused query"` when the brief requires them. Pass a catalog ID as the query to pin a chosen entry. Inspect `composition` and `execution_readiness` before building.
2. Read `blueprint.selected` and each `sections[].selected`. A section with `uses_blueprint` shares its evidence. Use the default `plan` export (`export.manifest`) or specify `--export-dir NEW_PRIVATE_DIRECTORY`; do not skip the exported source in favor of an invented implementation. Keep material private and respect upstream licensing, including required attribution. For each reference, record the exact catalog ID, source and asset URLs from `reference_contract`, and inspect the full `delivery.payload`, files and assets. Open `inspection.preview.path` and the original `visual_evidence.path` at the indicated time. Check the original asset against its catalog hash, or open the exact source and confirm that its asset and state belong to the reference. Record the composition, focal point, type scale, spacing, palette and motion before coding. If matching a screenshot, run `unfslop library "<visual intent>" --reference SCREENSHOT --full`.
3. Follow `delivery.tier` and `use.action`. For a `source_bundle` with `bundle_status: verified`, integrate the original files and assets at their intended paths and preserve the dependencies, revision and declared usage rights. For a `source_snapshot`, integrate the stored files, review dependencies, assets and usage rights, and preserve the observable layout and behavior. For a `build_specification`, implement the full prompt and preserve its specific design constraints. For a `registry_pointer`, review the license and obtain the actual registry source if authorized and compatible. Reconstruct visual references and descriptions from the available evidence. Use `--local` for plans limited to stored prompts, Skiper source snapshots and imported source bundles.
4. Treat `reference_contract.missing_evidence` as a list of prerequisites for a fidelity claim. Recover the exact material by ID or from its original URLs and verify it. For a pinned reference with unresolved evidence, report the blocked parts and avoid substituting generic sections, invented assets or unrelated motion. For a flexible selection, choose and document another verified reference. `comparison_required` means the materials are ready for comparison.
5. Render the result at matching viewport sizes and compare it side by side with the verified source image or corresponding video frames. Exercise the original interaction states and check timing, layout, typography, assets and motion. Report the build mode, reference IDs and exact URLs, the evidence used, the compared viewports and states, discrepancies and missing evidence. Claim fidelity only for the parts actually verified.

Start with `unfslop library` to page through the catalog, or `unfslop library "<query>"` for one component. Use `unfslop design "<query>"` when you need a short reference packet with two craft cards. Where the library reports lexical retrieval or a missing model, describe that outcome accurately.

## Get the relevant cards

Run `unfslop context "<action, surface, constraint>"` (default budget 2,000 estimated tokens, up to six cards). Use an explicit mode for mixed requests or a short English description of a non-English task. Keep product copy in the requested language. The examples below use the CLI on PATH. An installed copy can also run from the skill's `bin/` directory by absolute path. From a checkout, use `cargo run --locked --release --bin unfslop -- <command>` at the repository root.

| Task | CLI mode | Start here if the binary is unavailable |
| --- | --- | --- |
| Build a screen | `build` | [Surface intent](cards/imp.modes.md) |
| Find visual references | `inspire` | [Inspiration](cards/imp.inspiration.md) |
| Review a design | `critique` | [Critique](cards/imp.critique.md) |
| Polish existing UI | `polish` | [Polish](cards/imp.polish.md) |
| Work on shared tokens | `system` | [Design systems](cards/imp.system.md) |
| Fix focus or accessibility | `a11y` | [Accessibility](cards/imp.a11y.md) |
| Implement direct manipulation | `gesture` | [Direct manipulation](cards/apple.direct-manipulation.md) |
| Design a transition | `motion` | [Motion](cards/imp.motion.md) |
| Follow native conventions | `native` | [Platform principles](cards/apple.principles.md) |

Use `unfslop get <id>` for a specific rule, `unfslop cards` for the index, or open the linked card directly. Pull another only when the task reaches that subject.

Use the [catalog guide](cards/imp.inspiration.md) for preview and material details. Set `UNFSLOP_LIBRARY_DATA` to the private catalog and indexes and `UNFSLOP_MEDIA_ROOT` to any separate media directory. The installed skill loads EmbeddingGemma 2 through the configured Python environment. Use the reported backend when describing a result, and acknowledge when a source only provides text.

## Implement and verify

- Use the project's primitives and real content. Make the primary action discoverable at the narrowest supported width. For multilingual surfaces, test long labels, mixed-script values and the actual reading direction.
- Give controls native semantics, accessible names and visible focus. Provide immediate press feedback. Commit ordinary button actions on activation so pointer cancellation and keyboard use work. A draggable surface should track the pointer, accept interruption, and offer a non-drag path to the same outcome.
- Model states the flow can enter. For a failed save, retain the input, show the error next to the action and allow retry. For reduced motion, keep the final state and remove unnecessary travel.
- Run `unfslop lint <changed paths>` for supported web files. Inspect each finding in context. Exercise the main action and a relevant failure or cancellation path. Check the rendered screen at narrow and wide sizes, keyboard focus, contrast and motion preferences as applicable. Use the [craft floor](cards/imp.craft-floor.md) for details.
- Report the change and checks actually performed. For screenshot-only reviews, cite visible evidence and identify interaction checks that still need a live surface. Stop once the requested flow works and the observed defects are addressed.

Independent distillation of Emil Kowalski's Apple Design and Paul Bakaus' Impeccable. See the project's NOTICE.md for attribution.
