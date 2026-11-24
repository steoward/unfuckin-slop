---
name: unfuckin-slop
description: "Build web interfaces from a local model-ranked library of page prompts and UI components. Use when asked to build with unfuckin-slop or to search its catalog. Also supplies Apple Design and Impeccable guidance for UI refinement, interaction design and critique."
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

When asked to build a new site or screen with unfuckin-slop, use the library's selected material to build the page.

1. Run `unfslop plan "<product, primary action, interaction and layout constraints>"`. Use a concise English retrieval brief and keep the interface in the requested language. The default sections fit a product landing page. For other screens, name the required parts with repeated `--section "name=focused query"`. Pass a catalog ID as the query to pin a chosen entry.
2. Read `blueprint.selected` and each `sections[].selected`. Use the blueprint for layout, tokens and motion, then implement the sections in order. A section with `uses_blueprint` shares the blueprint material. Choose an alternative if it better fits the actual interaction or stack. For a missing section, search `unfslop library "<section interaction>"` or narrow by `--pool`, `--source` and `--category`.
3. Run `unfslop library --record ID --record ID` once with the chosen IDs to load their complete payloads. Use `plan --full` when you want selected payloads inline. Follow each `use.action`: adapt the stored build prompt, integrate the stored source and its dependencies, or review and install the registry entry in a compatible project. When registry access or the framework prevents installation, adapt the stored description or select a bundled source. Use `--local` to plan using bundled prompts and source snapshots only.
4. Use the actual product copy, data, assets and actions. Apply one set of design tokens across the selected pieces. Verify the rendered page and primary flow. Report which library entries were used and identify any section that required a fallback.

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

Use the [catalog guide](cards/imp.inspiration.md) for preview and material details. The installed `design-library/` includes the encoder, vector indexes and complete catalog payloads. Install its Python requirements in your working Python environment to enable hybrid search. A source checkout has the same requirements at the repository root.

## Implement and verify

- Use the project's primitives and real content. Make the primary action discoverable at the narrowest supported width. For multilingual surfaces, test long labels, mixed-script values and the actual reading direction.
- Give controls native semantics, accessible names and visible focus. Provide immediate press feedback. Commit ordinary button actions on activation so pointer cancellation and keyboard use work. A draggable surface should track the pointer, accept interruption, and offer a non-drag path to the same outcome.
- Model states the flow can enter. For a failed save, retain the input, show the error next to the action and allow retry. For reduced motion, keep the final state and remove unnecessary travel.
- Run `unfslop lint <changed paths>` for supported web files. Inspect each finding in context. Exercise the main action and a relevant failure or cancellation path. Check the rendered screen at narrow and wide sizes, keyboard focus, contrast and motion preferences as applicable. Use the [craft floor](cards/imp.craft-floor.md) for details.
- Report the change and checks actually performed. For screenshot-only reviews, cite visible evidence and identify interaction checks that still need a live surface. Stop once the requested flow works and the observed defects are addressed.

Independent distillation of Emil Kowalski's Apple Design and Paul Bakaus' Impeccable. See the project's NOTICE.md for attribution.
