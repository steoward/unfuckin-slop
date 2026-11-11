---
id: imp.states
title: States and edge cases — the half of the UI nobody draws
triggers: states, hover, focus, disabled, loading, error, empty, skeleton, edge cases, i18n, rtl, offline, error message, harden
pulls: imp.a11y, imp.copy
weight: 9
---

# Required states

For every interactive element: default, hover, active, focus-visible, disabled, loading, error. For every collection: empty, one item, many items, loading, error, no permission.

- **Loading** is not a spinner in the middle of a blank page. Use a skeleton that matches the final layout, or keep the previous content and show progress in place.
- **Empty states teach.** Say what would be here, why it is empty, and the one action that fills it.
- **Errors name the problem and the recovery.** "Could not save: the file is read-only. Duplicate it to continue." Not "Something went wrong."
- **Disabled needs a reason nearby.** A disabled control with no explanation is a dead end.
- **Optimistic UI needs a reversal path.** If the server can reject it, show it.

# Hardening

Real content is the test: long names, no name, 300 items, 0 items, 4-digit numbers, Arabic and Hebrew (RTL), German (30–40% longer), emoji in titles, missing images, slow 3G, offline, double submit, back button after mutation.

- **Layout must survive 200% zoom** and a 320px viewport.
- **Destructive actions** get confirm or undo, never both, never a modal for something reversible.
- **Never lose user input** on navigation, refresh, or error.
