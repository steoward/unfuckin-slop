---
id: imp.critique
title: Critique — the review format, and how to be honest in it
triggers: critique, review, feedback, design review, audit, score, heuristic, what works, findings, evaluate
pulls: imp.craft-floor, imp.bans, imp.slop-test
weight: 7
---

# Review format

1. **Verdict** in one sentence. For a live flow, summarize readiness and the blocking defect, if any. For a screenshot or source-only review, scope the verdict to the evidence available.
2. **Critical** — blocks shipping. Contrast failures, broken states, unreachable controls, layout that breaks at a real viewport.
3. **Improvements** — worth doing, ordered by impact.
4. **Craft notes** — the small things: optical alignment, timing, copy, focus ring.
5. **What works** — name it specifically, so it is not lost in the next pass.
6. **Platform notes** — only if native conventions are in play.

Each finding is three lines:

```
What:  <the observation, with a file/route and, where useful, a number>
Why:   <the principle, cited from the card that governs it>
Fix:   <the concrete change>
```

# Scoring

When scores are requested, score each observed axis (hierarchy, clarity, craft, accessibility, coherence) from 1–5 with a one-line justification. Mark untested axes as unverified. Name the highest-impact defect and how to confirm its fix.

# Rules

- Be honest. No praise padding, no "great job overall" before a list of failures.
- Review what is rendered, at the sizes it ships at. A screenshot can show clipping or competing actions. Keyboard travel, error recovery and animation interruption need a live interaction or a corresponding test.
- Do not rewrite the design unless asked; the review is the deliverable.
- Distinguish taste from defect. "I would have chosen another typeface" is not a finding; "tracking is -0.06em, letters touch" is.
