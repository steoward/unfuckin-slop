---
id: apple.multimodal
title: Multimodal feedback — causality, harmony, utility
triggers: haptics, sound, vibration, feedback, audio, vibration api, toggle, snap, success, error, notification
pulls: apple.response
weight: 4
---

# Multimodal feedback

Three rules for combining senses:

1. **Causality.** It must be obvious what caused the feedback. Trigger on the actual causal event (the toggle flipping, the item snapping home) and match its character to the action's physicality.
2. **Harmony.** Visual, sound, and haptic fire on the **same frame**. Latency between them destroys the illusion. Do not let a CSS transition lag the audio or the Vibration API call.
3. **Utility.** Add feedback only where it earns its place. Reserve haptics and sound for meaningful moments: success, error, commit, snap. Over-feedback trains people to ignore all of it.

On the web this is usually a silent no-op by design: sound and vibration without an explicit user gesture are blocked or hostile. Use it only in installable, deliberate contexts, and never as the only signal that something happened.
