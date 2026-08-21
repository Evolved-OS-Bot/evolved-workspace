# PEACH-LAYER Three-Quarter Layered Source v2 Failure Record

**Status:** Rejected by visual QA; preserved and never promoted  
**Build date:** 4 August 2026

Version 2 passed neutral technical recomposition with zero unassigned visible
pixels and zero differing rendered pixels. It nevertheless failed the required
isolated hidden-restoration inspection.

The fixed overlap capsules were too large and used an unfiltered average that
mixed peach fill with deep-plum outline pixels, producing visible brown circles.
The body clean-plate restoration also allowed eye and face colours to act as
clone donors, leaving patterned grey/cream restoration instead of clean warm-
peach texture beneath detachable face elements.

Preserved evidence:

- `outputs/evolved-heroine/animation/rigs/source/PEACH-LAYER-three-quarter-layered-source-v2/`
- `outputs/evolved-heroine/animation/review/layered-source/PEACH-LAYER-three-quarter-layered-source-v2-hidden-restoration-exposure.png`
- `outputs/evolved-heroine/animation/qa/runs/PEACH-LAYER-three-quarter-layered-source-v2/qa-report.json`

Version 3 must retain the exact neutral match while using component-specific
donor filters, smaller concealed capsules, and only warm-peach donors for the
body face field.
