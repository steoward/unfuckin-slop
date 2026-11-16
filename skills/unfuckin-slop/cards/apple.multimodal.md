---
id: apple.multimodal
title: Native mobile haptics — causality, harmony, utility
triggers: native haptics, mobile haptics, taptic engine, core haptics, device vibration, tactile haptic
pulls: apple.response
weight: 4
---

# Native tactile feedback

Three rules for hardware tactile pulses in native applications:

1. **Causality.** It must be obvious what caused the physical impulse. Trigger on the actual causal event (crossing a detent or committing an action) and match its intensity to the interaction.
2. **Harmony.** Visual and tactile impulses fire on the **exact same frame**. Latency between screen updates and hardware motors destroys the physical illusion.
3. **Utility.** Add tactile impulses only where they earn their place. Reserve hardware impulses for critical boundaries: physical threshold pass, item release, or state commit. Overuse desensitizes the hand.

> **CRITICAL PLATFORM BOUNDARY:** Hardware haptic motors belong exclusively to native mobile environments (e.g. iOS Core Haptics or Android HapticFeedback). Browser screens must remain completely calm; never inject artificial sensory effects into desktop or browser interfaces.
