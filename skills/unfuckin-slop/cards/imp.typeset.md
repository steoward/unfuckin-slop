---
id: imp.typeset
title: Typesetting — scale with real steps, one voice
triggers: typography, type, font pairing, scale, font size, line height, measure, headings, font loading, variable font
pulls: apple.typography, imp.craft-floor
weight: 8
---

# Typesetting

- **A scale with real steps.** 1.25–1.5 ratio between levels, not 16/17/18px. Body 16–18px, then jump.
- **Body measure 65–75ch.** Wider and the eye loses the line; narrower and the page feels nervous.
- **Line-height inverse to size.** 1.0–1.1 for display, 1.4–1.6 for body, 1.6–1.7 for long-form.
- **Tracking follows size.** Negative on display, near zero on body, slightly positive on small caps or tiny labels. Floor -0.04em.
- **Weight carries emphasis** before size does. Two weights of one family beat two families.
- **Two families maximum.** Usually one sans + one mono for code and data. A display face plus a text face is the other honest pairing; anything more is a collage.
- **Self-host, subset, and set `font-display: swap`.** A flash of invisible text is a regression, not a style.
- **Use variable fonts** where they exist: one file, real intermediate weights, no faux bold.
- **Never use the system display face as the brand voice** of an own-world page, and never ship faux italic or faux condensed.

# Failure modes

Sized-up body text pretending to be a heading. Centred long-form. Justified text without hyphenation. Tabular data in a proportional face. Letter-spacing applied globally.
