# PEACH-LAYER Three-Quarter Layered Source v5 Failure Record

**Status:** Rejected by visual QA; preserved and never promoted  
**Build date:** 4 August 2026

Version 5 introduced the correct clean-plate architecture: a restored body below
a fixed face-field texture correction and detachable face elements. The neutral
render remained pixel-exact.

The nearest-donor fill used beneath the face field produced visible radial bands
when isolated. Although those bands were hidden at neutral, they could appear
through a moved expression and do not meet the layered-source quality bar.

Version 6 retains the v5 layer architecture but replaces nearest-donor face
restoration with a smooth deterministic bilinear warm-peach field sampled from
four approved surrounding body patches.
