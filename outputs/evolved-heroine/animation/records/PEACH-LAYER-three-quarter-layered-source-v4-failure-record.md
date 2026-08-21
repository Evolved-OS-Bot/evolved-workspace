# PEACH-LAYER Three-Quarter Layered Source v4 Failure Record

**Status:** Rejected by visual QA; preserved and never promoted  
**Build date:** 4 August 2026

Version 4 retained zero unassigned pixels and zero neutral rendered-pixel
differences. A two-pixel expansion of the bounded face masks removed most
flattened antialias remnants.

The isolated body clean plate still retained a faint ghost of the original eyes
and mouth. Further mask expansion would carry increasingly large peach-coloured
patches with movable face elements and would not be a robust architecture.

Version 5 therefore separates a fixed `FACE-FIELD-TEXTURE-LOCKED` correction
layer from the clean body plate. The body can be fully restored beneath all
movable facial features, while the fixed correction layer restores the exact
approved neutral body texture outside those features.
