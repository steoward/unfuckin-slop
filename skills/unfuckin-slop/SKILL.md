---
name: unfuckin-slop
description: "Design, refine, and review web or native interfaces. Use the local design-reference model and Apple Design / Impeccable guidance for new screens, UI redesigns, visual critique, interaction and gesture design, accessibility, responsive layouts, or design-system work."
---

# Unfuckin-Slop

Start with the person using the screen. Identify their main action, what they need to see before acting, and what counts as success. In an existing app, inspect the component, its callers, nearby UI, and a rendered example when available.

## Choose the scope

| Request | First move | Deliverable |
| --- | --- | --- |
| New screen or redesign | Name the primary action and run the design brief below. Pick a surface intent (Persuade, Experience, Operate, Read). | A working screen with real hierarchy and a usable primary flow. |
| Refine or repair | Reproduce the issue. Reuse existing tokens, components, copy and interaction contracts. | The smallest coherent change that solves the observed problem. |
| Review | Identify the route, screenshot or files under review and the evidence each provides. | Findings ordered by impact. Edit only when requested. |
| Motion or system work | Isolate the gesture, state transition, token or shared primitive and inspect a real consumer. | A change verified in context, including recovery or fallback where applicable. |

Treat the user's brief and established product conventions as design inputs. Preserve factual claims, supported languages and working actions. For an open brief, pick one concrete organizing idea. On an inventory screen that could mean grouping by stock status with the next action alongside each exception. Decorative effects need a purpose on that surface.

## Build the design direction

For a new identity, page or substantial redesign, start with `unfslop design "<subject, primary action, visual or interaction constraint>"`. For a single new component add `--pool components`. The command returns up to three source records and one complete card from each design tradition. Use `--source` when the provider matters. Known titles, IDs and original URLs can resolve directly. Use a canonical ID if the packet reports more than one exact match.

1. Check `material.kind` and `material.excerpt_truncated`. Open a selected result with `unfslop design --record ID` (add `--pool components` for either component provider). A MotionSites prompt describes a build, a Skiper UI snapshot may need assets and helpers, and a 21st.dev entry points to a registry. Read the source text and distinguish these from working demos. Open the most useful source or video when visual inspection is available. A text description alone supports claims about the catalog text. A link alone supplies no evidence about what an animation feels like.
2. Sketch two plausible compositions using the product's real content. Select one by a concrete constraint such as comparing rows, previewing a surface, or reading uninterrupted. A distinctive gesture can be as important as a distinctive layout. Borrow one transferable relationship and identify what would fail if copied into this product. Skip weak references or re-query using the interaction rather than the industry.
3. Use the Impeccable card to challenge hierarchy, layout or copy, and the Apple card to refine perception, typography or interaction. Follow a related card when a decision crosses topics. Keep a short direction note while implementing: focal point, composition at wide and narrow widths, primary interaction and reference evidence. Respect the user's pinned visual language.
4. Inspect the rendered result with realistic content. Could you swap in an unrelated product name without changing the composition? If so, revisit the main design decision. At phone width, confirm that a distinctive preview leaves the primary choice discoverable. In a work queue, keep the field labels users need to compare rows.

Read `evidence.backend` to distinguish hybrid from lexical search. For `needs_specific_query`, supply an English description of the subject and interaction. For `unavailable`, use the diagnostic to restore the full library or use a supplied visual reference and the local cards. Describe fallback honestly. A small repair or a screenshot review can go directly to the relevant cards.

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

Use the [catalog guide](cards/imp.inspiration.md) for full source blueprints, videos and targeted searches. The installed `design-library/` includes the model and both catalogs. Install its Python requirements in your working Python environment to enable hybrid search. A source checkout has the same requirements at the repository root.

## Implement and verify

- Use the project's primitives and real content. Make the primary action discoverable at the narrowest supported width. For multilingual surfaces, test long labels, mixed-script values and the actual reading direction.
- Give controls native semantics, accessible names and visible focus. Provide immediate press feedback. Commit ordinary button actions on activation so pointer cancellation and keyboard use work. A draggable surface should track the pointer, accept interruption, and offer a non-drag path to the same outcome.
- Model states the flow can enter. For a failed save, retain the input, show the error next to the action and allow retry. For reduced motion, keep the final state and remove unnecessary travel.
- Run `unfslop lint <changed paths>` for supported web files. Inspect each finding in context. Exercise the main action and a relevant failure or cancellation path. Check the rendered screen at narrow and wide sizes, keyboard focus, contrast and motion preferences as applicable. Use the [craft floor](cards/imp.craft-floor.md) for details.
- Report the change and checks actually performed. For screenshot-only reviews, cite visible evidence and identify interaction checks that still need a live surface. Stop once the requested flow works and the observed defects are addressed.

Independent distillation of Emil Kowalski's Apple Design and Paul Bakaus' Impeccable. See the project's NOTICE.md for attribution.
