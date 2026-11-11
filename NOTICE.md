# Attribution

Unfuckin-Slop is an independent distillation, rewritten for retrieval. It is not a copy of either
source skill, and neither author endorses it.

## Apple Design

By Emil Kowalski, `github.com/emilkowalski/skills` (`apple-design`). It translates Apple's WWDC
interface talks to the web, chiefly:

- *Designing Fluid Interfaces* (WWDC 2018): response, direct manipulation, interruption, springs,
  velocity handoff, momentum projection, spatial consistency, rubber-banding.
- *The Details of UI Typography* (WWDC 2020): optical sizing, tracking, leading.
- *Principles of Great Design* (WWDC 2026): the eight principles.
- *Designing Audio-Haptic Experiences*: causality, harmony, utility.

The cards in this repository rewrite that material for one-question-at-a-time retrieval, keeping the
concrete numbers and code shapes. Apple's underlying material remains Apple's copyright.

## Impeccable

By Paul Bakaus, `github.com/pbakaus/impeccable`, Apache-2.0. It began from Anthropic's
frontend-design skill. The cards here take its direction discipline (brief wins, refinement preserves
and redesign replaces, the four modes), its craft floor, its absolute ban and refused defaults, and
its critique format.

## What was added

- The decomposition into 29 atom cards with trigger metadata, token costs and `pulls` edges.
- The retrieval layer: BM25 ranking, mode detection, budget enforcement, and the rule that a pack
  stops rather than padding itself with weak matches.
- The 18 deterministic lint rules, and the Rust implementation of all of the above.

If you want the full originals, install them at their sources. This project exists so an agent does
not have to load both to answer one question.
