---
id: apple.process
title: Process — prototype the interaction, not the picture
triggers: process, prototype, iteration, review, slow motion, testing, design together, interactive demo, spec
pulls: imp.workflow
weight: 5
---

# Process

- **Prototype interactively.** An interactive demo is worth a million static designs. You discover the interface by building and playing with it, and a working prototype sets a concrete bar that prevents a mediocre final implementation.
- **Design interaction and visuals together.** You should not be able to tell where one ends and the other begins. Motion is not a layer added after the pixels.
- **Test with real people in real context.** A demo on a 27-inch monitor with a mouse is not evidence about a phone held one-handed in sunlight.
- **Review motion with fresh eyes.** Play it in slow motion or frame-by-frame to catch what is invisible at full speed: the jump on interrupt, the seam at release, the element that starts from the wrong value.

# Deliverable shape

When the work is done, be able to state: the interaction model, the spring values used, what happens on interrupt, what happens at the boundary, and what the reduced-motion version is. If any of those is "it just eases in", the design is unfinished.
