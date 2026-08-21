# PEACH-LAYER Three-Quarter Layered Source v10 Review

**Status:** Awaiting Peter Brown layered-source decision  
**Approved visual target:** `PEACH-LAYER-three-quarter-candidate-v1`  
**Target SHA-256:** `3be0feb142374ba4ae9b1bf1dcdfde549cc56cde16188b3479548cce89b7ac9d`

## Decision requested

Approve `PEACH-LAYER-three-quarter-layered-source-v10` as the editable layered
source and identity base for Apple Motion rig construction.

This decision does not approve the Motion rig, provisional pivots, root-cover
masks, motions, expressions, templates, exports, deployment, publication or
contractor handoff.

## Technical result

- 29 named, full-canvas 1254 x 1254, 8-bit RGBA PNG layers.
- Every layer has an embedded sRGB profile.
- Zero unassigned source-visible pixels.
- Zero differing rendered pixels between the layered neutral recomposite and
  the exact approved visual target.
- OpenRaster package and a direct Motion-ingest PNG layer package are included.
- No horizontal flip or negative-X operation was used.
- `Evolved` remains locked only to the anatomical-left shoe, which is viewer-
  right at neutral. The anatomical-right shoe remains blank.
- Body rendering and shading remain one locked clean plate. A separate fixed
  face-field texture layer preserves exact neutral texture while leaving clean
  warm-peach pixels beneath detachable facial elements.

## Review files

- `PEACH-LAYER-three-quarter-layered-source-v10-neutral-difference.png`
  compares the approved target, layered recomposite and difference result.
- `PEACH-LAYER-three-quarter-layered-source-v10-exploded-components.png`
  shows the functional groups independently.
- `PEACH-LAYER-three-quarter-layered-source-v10-hidden-restoration-exposure.png`
  exposes the deterministic leaf, limb and body restoration that is concealed
  in the approved neutral pose.
- `PEACH-LAYER-three-quarter-layered-source-v10-light-dark-checker.png`
  checks the exact neutral recomposite on three backgrounds.
- `PEACH-LAYER-three-quarter-layered-source-v10-articulation-stress-sheet-v2.png`
  is a mechanics preview only and is not rig approval.

## Mandatory rig follow-up

The source stress test found that a 12-degree outward leg-root rotation exposes
background wedges at the shorts openings with both provisional root pivot
heights tested. This is recorded, not concealed.

The Motion rig must add and visually verify native root-cover masks or equivalent
linked cover behaviour before it can pass its separate approval gate. Approving
the layered source does not approve either provisional leg-root pivot or this
unresolved rig mechanic.

## Preserved rejected iterations

Versions 1 through 9 remain preserved with failure records. They were rejected
for unassigned pixels, poor hidden-fill colours, face remnants, banded clean-
plate restoration, leg-root stress gaps, or neutral alpha changes. None was
promoted.

## Approval wording

Use:

> Approve PEACH-LAYER-three-quarter-layered-source-v10 as the editable layered
> source and identity base for Apple Motion rig construction. This does not
> approve the rig, provisional pivots, root-cover masks, motions, expressions,
> templates, exports, or deployment.

If rejected, identify the exact layer, clean-plate, face-field, overlap,
laterality, apparel, glove, leaf, shoe or branding correction required.
