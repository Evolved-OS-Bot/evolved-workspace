# Peach Animation Production System

**Status:** In progress; corrected layered source v11 approved and Motion rig integration resuming  
**Canonical specification:** `reference/evolved-heroine/animation-system.md`  
**Execution brief:** `plans/2026-08-04-peach-animation-project.md`

This directory contains the versioned production system for Peach animation.
Approved static masters remain read-only and outside this directory.

## Approved visual target

The current approval target is:

`PEACH-LAYER-three-quarter-candidate-v1`

Peter Brown approved this artifact on 4 August 2026 as the neutral visual target
for full layered construction. The approval does not approve the layered source,
editable Motion rig, any reusable motion, any expression, or any deployment.

Review:

- `review/layered-reconstruction/PEACH-LAYER-three-quarter-candidate-v1-light-dark-checker.png`
- `review/layered-reconstruction/PEACH-LAYER-three-quarter-candidate-v1-source-comparison.png`
- `review/layered-reconstruction/PEACH-LAYER-three-quarter-candidate-v1-review.md`

## Approved layered identity base

`PEACH-LAYER-three-quarter-layered-source-v10` has 29 full-canvas RGBA sRGB
layers and an exact neutral rendered-pixel match to the approved visual target.
Peter Brown approved it on 4 August 2026 as the editable layered source and
identity base for Apple Motion rig construction.

The exact approved copy is:

`rigs/approved/PEACH-LAYER-three-quarter-layered-source-v10/`

This approval does not approve the rig, provisional pivots, root-cover masks,
motions, expressions, templates, exports, or deployment.

### Source correction gate

The enlarged transparent-viewer inspection later revealed low alpha baked into
the distressed shoe fabric and both tongues. The defect is in the approved
visual target and v10 source, not in Motion. Approved v10 remains frozen as the
historical identity base, but new rig construction is paused.

`PEACH-LAYER-three-quarter-layered-source-v11` is the non-destructive
correction. It changes alpha only inside audited inset shoe regions, keeps all
27 non-shoe layers byte-identical, and keeps the locked `Evolved` brand layer
byte-identical. Peter approved it on 4 August 2026 as the corrected editable
layered source and identity base for Apple Motion rig construction.

The exact approved copy is:

`rigs/approved/PEACH-LAYER-three-quarter-layered-source-v11/`

V11 supersedes v10 for new rig work. The approved v10 package remains preserved
as immutable historical evidence.

Correction review:

- `review/layered-source/PEACH-LAYER-three-quarter-layered-source-v11-shoe-opacity-review.png`
- `review/layered-source/PEACH-LAYER-three-quarter-layered-source-v11-light-dark-checker.png`
- `review/layered-source/PEACH-LAYER-three-quarter-layered-source-v11-review.md`

The source stress preview exposed a mandatory Motion follow-up: native root-
cover masks or equivalent linked behaviour must close the leg-opening wedges
before the rig can pass its separate approval gate.

Review:

- `review/layered-source/PEACH-LAYER-three-quarter-layered-source-v10-neutral-difference.png`
- `review/layered-source/PEACH-LAYER-three-quarter-layered-source-v10-exploded-components.png`
- `review/layered-source/PEACH-LAYER-three-quarter-layered-source-v10-hidden-restoration-exposure.png`
- `review/layered-source/PEACH-LAYER-three-quarter-layered-source-v10-light-dark-checker.png`
- `review/layered-source/PEACH-LAYER-three-quarter-layered-source-v10-review.md`

## Current rig phase

The native three-quarter Motion ingest is complete. All 29 approved layers are
separate, ordered and protected as required. Motion's supported Save Current
Frame path produced 16-bit/color transparent RGBA sRGB exports from the layered
stack and a separate single-neutral reference. They are byte-identical with
zero RGB or alpha differences, so the strict neutral gate has passed.

The reversible anatomical-right upper-leg pivot passes neutral transform
compensation exactly at provisional source-canvas coordinate `(582, 680)`.
This work is preserved. The native Motion stack must now be relinked or rebuilt
from approved v11 and neutral transparency reverified before root-cover
construction.

The import-ready scaffold is:

`rigs/working/PEACH-RIG-three-quarter-candidate-v1/`

Native construction is now active in Apple Motion 6.3 after Peter enabled
Accessibility control. Peter fixed **30 fps** as the canonical phase-one frame
rate on 4 August 2026. This timing decision does not approve any rig mechanic,
motion, expression, template or export.

## Production controls

- Never overwrite an approved static master.
- Never horizontally flip Peach.
- Anatomical left and right are named explicitly in every layer and control.
- `Evolved` belongs only to the outward-facing panel of the anatomical left
  shoe and is absent when that panel is hidden.
- Technical QA and human visual approval are separate.
- Candidate, rejected, superseded, and approved versions remain preserved.
- No candidate is promoted without an approval record tied to its exact hash.

## Directory map

```text
records/       Environment, feasibility, and dependency evidence
manifests/     Source, project, version, approval, and release records
rigs/          Layered construction and Motion rig sources
motions/       Candidate and approved reusable motions
renders/       Transparent, social, website, and video outputs
templates/     Motion, Final Cut Pro, and channel composition templates
qa/            Schemas, baselines, and run evidence
review/        Human review packages
handoff/       Local-only external-animator package preparation
```
