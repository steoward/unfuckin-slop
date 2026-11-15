---
id: imp.slop-test
title: The AI slop test — read the tells, then remove one thing
triggers: slop, generic, bland, template, ai generated, purple gradient, tells, boring, look like every app, sameness
pulls: imp.bans, imp.layout
weight: 8
---

# The tells

A page is slop when you can predict the next section from the previous one.

- Everything centred, every section the same width, every gap the same.
- Three equal feature cards with line icons, repeated.
- Purple-to-blue gradient hero, glass cards, big rounded corners, soft shadow.
- Emoji or generic line icons standing in for a drawn icon system.
- Hero headline "Elevate your workflow", subhead restating it, two buttons, one filled one ghost.
- All copy in the same weight; hierarchy carried only by font size.
- One identical fade-up on every section, `transition: all 300ms ease`.
- Zero states: no empty, no error, no loading, no focus ring.
- Decorative motion with no causal relation to the interaction.
- The page has no opinion about light, material, or type.

# The test

1. Cover the logo. Could this be any product in the category? If yes, the design is not deciding anything.
2. Name the axis you are deciding: structure, type, colour, material, or motion. One is enough, but it must be visible in the first viewport.
3. Commit, then **remove one thing**. The extra gradient, the extra card row, the extra border. Subtraction is the cheapest way out of the template.
4. Re-check the craft floor. Bold choices do not excuse broken contrast or missing states.

# What is NOT slop: Authored 3D & Kinetic Experiences

**3D Canvas, WebGL, particle fields, ambient lighting, and liquid glass are NOT slop when authored as the central interactive experience in `Experience` or `Persuade` modes.**

The difference between slop and craft is intentionality and physical causality:
- **Slop:** A generic template of three white cards with a purple-to-blue linear gradient and random floating blur blobs that ignore user input.
- **Craft:** An interactive Three.js particle canvas reacting to cursor physics, a 3D bento grid with spring tilt (`perspective: 1200px`), dynamic specular lighting, or liquid glass refraction computed on pointer coordinates.
- **Rule of thumb:** If the immersive 3D/kinetic element reacts dynamically to user physics at 60fps and defines the visual world, it is the creative anchor, not slop.
