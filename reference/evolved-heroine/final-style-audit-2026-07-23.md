# Final Style-Lock Audit

**Date:** 23 July 2026  
**Scope:** CHR007–CHR008, ACH001–ACH008, CEL001–CEL008 and FRD001–FRD008  
**Status:** Complete; all 26 v3 masters approved, promoted locally and live in Drive

## Audit Result

All 26 previous masters failed the final style lock introduced through the Cute v3 correction. Their earlier v2 pass removed the glossy animated rendering, but the peach bodies remained too circular and the cream, coral and deep-plum value separation was weaker than the locked Foundation Strength references.

The original approved v2 masters and Drive files were not overwritten during generation or review. They were replaced only after Peter approved the completed batch.

## Correction References

- CUT001 v3: closest finished implementation benchmark for the locked treatment; not a style authority
- FND002: tapered peach construction, paired lower lobes and pointed lower centre
- FND004: hard cream, peach, coral and deep-plum value separation
- FUN003: supporting palette, facial treatment and vintage ink finish

The eight original Approved Visual Calibration Set masters in `README.md` remain the only character identity and rendering-style authorities. CUT001 v3 demonstrates a successful application of those rules to a later category but cannot redefine them.

## Correction Outcome

All 26 assets were regenerated with their original pose, expression, gesture, apparel and props preserved. The correction applied:

- Full upper peach lobes with a clear top cleft
- Strong inward taper below the widest point
- Paired lower lobes meeting at a pointed lower centre
- Hard cream highlight, warm peach base and coral-red mid-shadow
- Dark-plum lower and viewer-right shadow treatment with carved-print slashes
- Flat hand-inked 2D athletic-mascot rendering
- Exact `Evolved` wordmark on the outside of the anatomical left shoe only
- Transparent background with no floor, cast shadow or chroma fringe

CHR007 initially inherited a barbell from a strength reference. It was rejected and regenerated with prop-free Cute v3 references before the batch was closed.

ACH002 was normalized non-destructively onto the standard square canvas. A one-pixel edge artifact on CHR008 and 15 isolated blue fringe pixels on ACH002 were removed without changing the character artwork.

## Candidate Locations

Transparent candidates:

```text
outputs/evolved-heroine/candidates/final-style-lock/batch-2026-07-23/transparent-v3/
```

Review sheets:

```text
outputs/evolved-heroine/candidates/final-style-lock/batch-2026-07-23/review-sheets/
```

Original blue generation sources:

```text
outputs/evolved-heroine/candidates/final-style-lock/batch-2026-07-23/source-blue/
```

## Technical QA

All 26 current candidates passed:

- 1254 × 1254 pixels
- RGBA PNG
- Alpha range from fully transparent to fully opaque
- Four fully transparent corners
- No remaining chroma-blue pixels
- Correct asset count and category coverage

## Generation Prompt Set

The built-in image-generation workflow was used once per asset. Each prompt labelled the existing master as the pose-only target, CUT001 v3 as the closest finished implementation benchmark, FND002 as the construction authority, FND004 as the value-separation authority and FUN003 as supporting palette and ink authority.

Every prompt preserved the target's pose and props while requiring the tapered peach construction, hard cream/peach/coral/deep-plum graphic values, sparse carved-print slashes, 2D vintage rendering and one-left-shoe wordmark lock. Each source was generated on a flat blue chroma background and converted locally to transparent RGBA.

## Approval and Processing

On 23 July 2026, Peter Brown visually approved CHR008, ACH001–ACH008, CEL001–CEL008 and FRD001–FRD008: 25 assets in total.

Peter Brown approved the corrected prop-free CHR007 on 23 July 2026, completing approval of all 26 assets.

Processing completed on the same date:

1. All 26 v2 masters were moved to `outputs/evolved-heroine/superseded/final-style-lock-2026-07-23/`.
2. The stray FRD001 v1 duplicate was moved into the same superseded archive.
3. All 26 transparent v3 PNGs were promoted to `outputs/evolved-heroine/approved/`.
4. All 26 existing Drive PNG files were replaced in place and renamed with the v3 suffix.
5. Drive file IDs, category folders and spreadsheet asset links were preserved.
6. All 26 local asset records were updated to v3.

Google prompt documents were not changed or uploaded during this PNG-only processing pass.
