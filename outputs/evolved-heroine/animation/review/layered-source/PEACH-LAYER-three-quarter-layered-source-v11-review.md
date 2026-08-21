# PEACH-LAYER-three-quarter-layered-source-v11 review

**Status:** Technical QA passed; human layered-source approval pending  
**Scope:** Corrected editable source only  
**Supersedes if approved:** `PEACH-LAYER-three-quarter-layered-source-v10`

## What changed

The enlarged transparent-viewer inspection revealed checkerboard showing
through the distressed fabric of the anatomical-right blank shoe and through
both shoe tongues. The same alpha topology exists in the original approved
visual target and v10 neutral recomposite, so this was a source defect rather
than an Apple Motion setting.

V11 is a deterministic alpha-only correction:

- 3,822 repaired pixels in `52-ANAT-R-SHOE-BLANK`
- 933 repaired pixels in `53-ANAT-L-SHOE-ART`
- 4,755 repaired pixels total
- no RGB changes to either shoe layer
- no alpha or RGB changes outside the audited inset shoe regions
- all 27 non-shoe layers byte-identical to approved v10
- locked `54-EVOLVED-BRAND-LOCKED` byte-identical to approved v10
- no horizontal flip or anatomy change

The approved v10 package was not overwritten.

## Review evidence

1. `PEACH-LAYER-three-quarter-layered-source-v11-shoe-opacity-review.png`
   shows v10 and v11 at 200% over checkerboard, plus the exact alpha repair mask.
2. `PEACH-LAYER-three-quarter-layered-source-v11-light-dark-checker.png`
   shows the complete corrected neutral on light, dark, and checker backgrounds.
3. `qa/runs/PEACH-LAYER-three-quarter-layered-source-v11/qa-report.json`
   records the technical invariants and pending human gate.

## Approval boundary

Approval promotes v11 only as the corrected editable layered source and
identity base for Apple Motion rig construction. It does not approve the
current rig, provisional pivots, root-cover masks, motions, expressions,
templates, exports, or deployment.

Suggested decision wording:

> Approve PEACH-LAYER-three-quarter-layered-source-v11 as the corrected editable
> layered source and identity base for Apple Motion rig construction. This
> approval is limited to the shoe-opacity correction and does not approve the
> rig, provisional pivots, root-cover masks, motions, expressions, templates,
> exports, or deployment.
