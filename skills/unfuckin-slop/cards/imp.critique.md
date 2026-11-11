---
id: imp.critique
title: Critique — the review format, and how to be honest in it
triggers: critique, review, feedback, design review, audit, score, heuristic, what works, findings, evaluate
pulls: imp.craft-floor, imp.bans, imp.slop-test
weight: 7
---

# Review format

1. **Verdict** in one sentence: ships, ships with fixes, or does not ship.
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

Score 1–5 with a one-line justification each: hierarchy, clarity, craft, accessibility, coherence. Do not average them into a single number; the weakest axis is the verdict.

# Rules

- Be honest. No praise padding, no "great job overall" before a list of failures.
- Review what is rendered, at the sizes it ships at. Source-only review misses overflow and contrast.
- Do not rewrite the design unless asked; the review is the deliverable.
- Distinguish taste from defect. "I would have chosen another typeface" is not a finding; "tracking is -0.06em, letters touch" is.
