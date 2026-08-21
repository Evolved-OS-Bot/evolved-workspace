# PEACH-RIG Three-Quarter v10 Architecture Contract

**Contract:** `PEACH-RIG-three-quarter-layered-source-v10-architecture-contract-v1`  
**Approved source:** `rigs/approved/PEACH-LAYER-three-quarter-layered-source-v10`  
**Status:** Candidate contract for Motion construction  
**Approval boundary:** Every pivot, control range and leg-root cover is provisional pending the separate rig approval.

## Purpose

This contract defines the first Apple Motion rig build from layered-source v10.
It does not approve the rig, pivots, cover masks, motions, expressions,
templates or exports.

The machine-readable contract is:

`PEACH-RIG-three-quarter-layered-source-v10-architecture-contract-v1.json`

## Canonical hierarchy and z-order

Back to front:

1. Leaf A, Leaf B and stem
2. Anatomical-right and anatomical-left upper arms
3. Anatomical-right and anatomical-left leg chains
4. Provisional fixed body-space leg-root covers
5. Shorts
6. Locked peach body and shading
7. Locked face-field texture
8. Eyes, pupils, brows, cheeks, nose and neutral mouth
9. Linked lower arms and gloves
10. Anatomical-right blank shoe
11. Anatomical-left shoe art and its locked `Evolved` child

Upper arms remain behind the body. Lower arms use linked transform proxies above
the body so later approved coaching gestures can cross the fruit without moving
the upper-arm attachment in front.

## Provisional pivots

All coordinates use the 1254 x 1254 source canvas and remain provisional.

| Control point | X | Y |
| --- | ---: | ---: |
| Character root | 642 | 1075 |
| Body | 644 | 440 |
| Stem | 642 | 230 |
| Leaf A | 614 | 226 |
| Leaf B | 670 | 226 |
| Anatomical-right arm root | 469 | 583 |
| Anatomical-right arm bend | 460 | 638 |
| Anatomical-right glove cuff | 448 | 690 |
| Anatomical-left arm root | 796 | 565 |
| Anatomical-left arm bend | 812 | 636 |
| Anatomical-left glove cuff | 821 | 693 |
| Anatomical-right leg root | 582 | 680 |
| Anatomical-right leg bend | 582 | 810 |
| Anatomical-right shoe cuff | 579 | 904 |
| Anatomical-left leg root | 678 | 680 |
| Anatomical-left leg bend | 706 | 811 |
| Anatomical-left shoe cuff | 739 | 910 |

The lower leg-root alternatives at Y 704 were tested and also exposed wedges.
Neither Y 680 nor Y 704 is approved before the Motion root-cover test passes.

## Deformation ownership

- The character root owns global position, positive uniform scale, rotation and
  opacity.
- The body driver owns settle, restrained tilt and no more than two percent
  reciprocal squash and stretch.
- Body deformation moves limb-root locators but never scales tube limbs into
  human anatomy.
- Each upper arm owns its root rotation. Each lower arm owns its bend and is
  linked to the upper-arm endpoint.
- Each upper leg owns its root rotation. Each lower leg owns its bend and the
  shoe inherits the lower-leg endpoint. The root covers remain fixed children
  of the body driver and do not inherit leg rotation by default.
- Leaves and stem own only their local rotations.
- Pupils own safe X and Y movement inside the fixed eye shapes.
- Brows own small vertical offsets.
- The body paint, shading, face-field texture and nose remain locked against
  freeform deformation.
- The `Evolved` layer inherits the anatomical-left shoe transform and has no
  independent control.

## Published controls for rig review

The first rig review publishes direct, bounded controls:

- Positive uniform scale: 25 to 200 percent
- Body settle: -20 to +20 pixels
- Body tilt: -4 to +4 degrees
- Body squash and stretch: normalized -1 to +1, limited to two percent
- Each arm root: -20 to +20 degrees
- Each arm bend: -20 to +20 degrees
- Each leg root: -12 to +12 degrees
- Each leg bend: -15 to +15 degrees
- Gaze X: -8 to +8 pixels
- Gaze Y: -6 to +6 pixels
- Each brow lift: -6 to +6 pixels
- Each leaf: -8 to +8 degrees
- Stem: -4 to +4 degrees

Root-cover mask tuning and any conditional fallback rotation link, independent
scale axes, layer opacity, brand transforms and QA overlays stay internal and
unpublished.

These are rig-review ranges, not approved motion ranges. Any later expansion
requires a new mechanics test.

## Neutral zero-state

The exact v10 neutral is the zero state of every published control.

- Global position and rotation: 0
- Global uniform scale: 100 percent
- Body settle, tilt and squash: 0
- All limb, leaf and stem rotations: 0
- Gaze and brow offsets: 0
- Mouth: neutral
- Root-cover rotation: 0; root-cover scale: 100 percent

Moving anchor points must use transform compensation so no imported pixel
moves. A neutral flatten must have zero differing rendered pixels from the v10
neutral recomposite.

Motion's normal parameter Reset returns each control to its imported default.
Do not simulate a reset button with a checkbox.

## Laterality and no-flip guards

At neutral:

- Anatomical left is viewer-right.
- Anatomical right is viewer-left.
- The viewer-right anatomical-left shoe owns the locked `Evolved` artwork.
- The viewer-left anatomical-right shoe is blank and has no brand child.

All group and control names use anatomical left or right. Directional gestures
must be built independently.

Only one positive uniform scale control may be published. Do not publish Scale
X or Scale Y, apply a Flip filter, use negative scale in a Link behaviour, or
create a mirrored rig state.

## Native Motion leg-root cover design

The v10 source test exposed background wedges inside both shorts openings at a
12-degree outward leg-root rotation. Wider source capsules alone did not solve
the problem.

Each leg receives a native Motion socket-cover group:

1. Clone the approved neutral upper-leg layer.
2. Apply one tight interior Bezier mask directly to the duplicate, limiting it
   to the shorts socket and excluding the deep-plum exterior contour.
3. Keep the cover fixed in body/pelvis space with 100 percent X and Y scale and
   zero rotation.
4. Place it above the rotating upper- and lower-leg chain but below the fixed
   shorts and body.
5. Do not link it to leg rotation by default.

Only if the tuned static cover fails one or more stress angles may the builder
add a conditional Link behaviour, initially following 50 percent of the
corresponding leg-root rotation. That half-angle follower is a fallback, not
the canonical default, and requires renewed review. Scale remains 100 percent.

Initial mask points are recorded exactly in the JSON contract. They are
provisional and may be tuned only inside the rig build.

Acceptance requires:

- No wedge at -12, -6, 0, +6 or +12 degrees
- At least 8 pixels of cover-to-leg alpha overlap at every test angle
- No double outline or visible cover at neutral
- No peach stub, human thigh shape or shorts deformation
- No cover pixels below canvas Y 782
- Clean combined tests with body tilt and two percent squash

The cover uses native Clone Layer, Bezier Mask and Link behaviour objects.
No source PNG or approved master is altered.

## Rig approval gate

The rig review must show:

- Neutral exact comparison
- Provisional pivots and anatomy overlay
- Arm-root and bend extremes
- The complete five-position leg-root sweep
- Root covers isolated and hidden in the final composite
- Leg-bend extremes
- Leaf, stem and pupil safe ranges
- Anatomical-left shoe branding close-up
- Light, dark plum and checkerboard renders

Rig approval approves only the selected pivots, cover behaviour and tested
control ranges. Each reusable motion and expression still requires its own
approval.
