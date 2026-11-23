---
name: unfuckin-slop
description: "Design, refine, and review web or native interfaces. Use for new screens, UI redesigns, visual critique, interaction and gesture design, accessibility, responsive layouts, or design-system work."
---

# Unfuckin-Slop

Start with the person using the screen. Identify their main action, what they need to see before acting, and what counts as success. In an existing app, inspect the component, its callers, nearby UI, and a rendered example when available.

## Choose the scope

| Request | First move | Deliverable |
| --- | --- | --- |
| New screen or redesign | Pick a surface intent from `imp.modes` (Persuade, Experience, Operate, Read). Use the brief, content and references to choose a direction. | A working screen with real hierarchy and a usable primary flow. |
| Refine or repair | Reproduce the issue. Reuse existing tokens, components, copy and interaction contracts. | The smallest coherent change that solves the observed problem. |
| Review | Identify the route, screenshot or files under review and the evidence each provides. | Findings ordered by impact. Edit only when requested. |
| Motion or system work | Isolate the gesture, state transition, token or shared primitive and inspect a real consumer. | A change verified in context, including recovery or fallback where applicable. |

Treat the user's brief and established product conventions as design inputs. Preserve factual claims, supported languages and working actions. For an open brief, pick one concrete organizing idea. On an inventory screen that could mean grouping by stock status with the next action alongside each exception. Decorative effects need a purpose on that surface.

## Get the relevant cards

Run `unfslop context "<action, surface, constraint>"` (default budget 2,000 estimated tokens, up to six cards). Use an explicit mode for mixed requests or a short English description of a non-English task. Keep product copy in the requested language. The examples below use the CLI on PATH. An installed copy can also run from the skill's `bin/` directory by absolute path. For the current checkout's router, build with `cargo build --release --bin unfslop` at the repository root.

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

## Choose references deliberately

For a new visual direction, consult the supplied references or query the showcase index from the **repository root**. Use the [search examples](cards/imp.inspiration.md) to choose between complete designs, individual components and token presets. Extract one decision you can apply, such as a product comparison that keeps prices aligned as titles wrap. A focused repair usually has a better reference in a sibling component. The standalone skill installation includes cards and a router. If the Python index is unavailable, proceed with the product, the brief and the cards.

## Implement and verify

- Use the project's primitives and real content. Make the primary action discoverable at the narrowest supported width. For multilingual surfaces, test long labels, mixed-script values and the actual reading direction.
- Give controls native semantics, accessible names and visible focus. Provide immediate press feedback. Commit ordinary button actions on activation so pointer cancellation and keyboard use work. A draggable surface should track the pointer, accept interruption, and offer a non-drag path to the same outcome.
- Model states the flow can enter. For a failed save, retain the input, show the error next to the action and allow retry. For reduced motion, keep the final state and remove unnecessary travel.
- Run `unfslop lint <changed paths>` for supported web files. Inspect each finding in context. Exercise the main action and a relevant failure or cancellation path. Check the rendered screen at narrow and wide sizes, keyboard focus, contrast and motion preferences as applicable. Use the [craft floor](cards/imp.craft-floor.md) for details.
- Report the change and checks actually performed. For screenshot-only reviews, cite visible evidence and identify interaction checks that still need a live surface. Stop once the requested flow works and the observed defects are addressed.

Independent distillation of Emil Kowalski's Apple Design and Paul Bakaus' Impeccable. See the project's NOTICE.md for attribution.
