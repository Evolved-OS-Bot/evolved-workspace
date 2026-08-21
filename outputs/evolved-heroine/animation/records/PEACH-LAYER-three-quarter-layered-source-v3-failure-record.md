# PEACH-LAYER Three-Quarter Layered Source v3 Failure Record

**Status:** Rejected by visual QA; preserved and never promoted  
**Build date:** 4 August 2026

Version 3 retained zero unassigned pixels and an exact neutral rendered-pixel
match. Its smaller, component-coloured overlap capsules corrected the v2 brown-
fill failure.

The isolated body clean plate still showed eye and mouth antialias remnants.
The first-pass facial masks selected core ink, cream and blush colours but did
not fully capture blended edge pixels from the flattened source. Those remnants
could become visible when a pupil, eye or mouth state moves, so v3 is not a valid
rig source.

Preserved evidence:

- `outputs/evolved-heroine/animation/rigs/source/PEACH-LAYER-three-quarter-layered-source-v3/`
- `outputs/evolved-heroine/animation/review/layered-source/PEACH-LAYER-three-quarter-layered-source-v3-exploded-components.png`
- `outputs/evolved-heroine/animation/qa/runs/PEACH-LAYER-three-quarter-layered-source-v3/qa-report.json`

Version 4 expands only the already hand-bounded facial feature masks by two
pixels to capture flattened antialias fringes. The neutral composite must remain
pixel-exact.
