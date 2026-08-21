# PEACH-LAYER Three-Quarter Layered Source v1 Failure Record

**Status:** Rejected by technical QA; preserved and never promoted  
**Build date:** 4 August 2026

The first deterministic separation pass failed closed because 6,474 visible
source pixels fell outside its initial semantic masks. A `99-QA-UNASSIGNED-
VISIBLE` layer preserved those pixels so the failure could be inspected without
losing approved artwork.

The neutral recomposite also reported 3,004 differing RGBA bytes with a maximum
channel delta of 17. Inspection established that this comparison included RGB
values beneath fully transparent pixels, but the build remains rejected because
the unassigned semantic layer is independently disqualifying.

Preserved package:

`outputs/evolved-heroine/animation/rigs/source/PEACH-LAYER-three-quarter-layered-source-v1/`

The v2 builder replaces the residual layer with deterministic nearest-semantic
assignment for path-edge antialias pixels and compares only rendered pixels
while still checking alpha everywhere. No approved source or static master was
changed.
