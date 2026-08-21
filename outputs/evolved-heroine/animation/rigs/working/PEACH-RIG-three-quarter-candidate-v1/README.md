# PEACH-RIG Three-Quarter Candidate v1 Build Scaffold

**Status:** Approved-v11 native ingest and exact supported neutral parity passed; right-leg pivot neutral pass; root-cover canary pending  
**Approved identity base:** `PEACH-LAYER-three-quarter-layered-source-v11`  
**Canonical application:** Apple Motion 6.3

This directory stages the first native Motion rig build without changing the
approved layered source. It is not an Apple Motion project, rig approval,
motion, template, export approval, or deployment package.

## Current execution boundary

Peter enabled Accessibility UI control to the automation host and fixed
**30 fps** as the canonical phase-one rate on 4 August 2026. Motion 6.3 created
the native project through its graphical interface. Hand-authored Motion XML
remains prohibited because Apple does not document that as a production
construction route.

The timing decision does not approve the rig, provisional pivots, root-cover
masks, motions, expressions, templates, exports or deployment.

The native v11 pivot canary contains all 29 approved layers as separate stills
in the exact manifest order. Motion's supported Save Current Frame path
produced 16-bit/color transparent RGBA sRGB exports from both the v11 layered
stack and a separate v11 single-neutral reference. The files are
byte-identical, with zero RGB or alpha differences. This also proves that the
approved 4,755-pixel shoe opacity correction survives the supported Motion
render path.

The provisional anatomical-right upper-leg pivot at source-canvas coordinate
`(582, 680)` is stored as Motion anchor `(-45, -53)` with matching position
compensation. Its supported neutral export remains byte-identical to the proven
neutral. The native source-derived root-cover mask and rotated stress grid are
still pending. Evidence:

`../../../qa/runs/PEACH-RIG-three-quarter-v11-pivot-canary-v1/qa-report.json`

## Source and contract

- Approved source:
  `../../approved/PEACH-LAYER-three-quarter-layered-source-v11/`
- Approval index:
  `../../approved/PEACH-LAYER-three-quarter-layered-source-v11-approval-index.json`
- Rig architecture:
  `../../source/analysis/PEACH-RIG-three-quarter-layered-source-v10-architecture-contract-v1.json`
- Native build note:
  `../../../records/PEACH-MOTION-native-rig-build-note-v1.md`
- Ordered build manifest:
  `rig-build-manifest.json`

## First native canary

1. Create a 1254 × 1254 transparent Standard Gamut SDR composition at 30 fps.
2. Import every approved PNG as a separate still with Image Sequence disabled.
3. Arrange the exact back-to-front stack in `rig-build-manifest.json`.
4. Lock the body/shading, face-field texture and left-shoe brand layers.
5. Export a full-resolution transparent neutral PNG.
6. Compare it with the approved neutral recomposite.
7. Stop unless the comparison has zero differing visible pixels.
8. Build one upper-leg pivot and its fixed, directly masked body-space root
   cover.
9. Test neutral, ±6 degrees, ±12 degrees and modest overtravel on checker,
   light and dark backgrounds.

The canonical candidate filename, once created natively, is:

`PEACH-RIG-three-quarter-candidate-v1.motn`
