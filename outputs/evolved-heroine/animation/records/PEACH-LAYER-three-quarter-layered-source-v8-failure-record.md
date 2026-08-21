# PEACH-LAYER Three-Quarter Layered Source v8 Failure Record

**Status:** Rejected by neutral technical QA; preserved and never promoted  
**Build date:** 4 August 2026

Version 8's tapered hidden leg extensions introduced 98 rendered-pixel
differences in the transparent centre gap between the legs, bounded by
`[618,687,649,737)`. The build failed closed before review generation.

Version 9 retains the tapered extensions but adds width only toward each outer
leg opening. The inner edges remain aligned with the source-visible legs.
