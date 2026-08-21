# Peach Motion native rig build note v1

- Created: 2026-08-04T15:31:00+10:00
- Scope: engineering audit and reversible build plan only
- Source package: `PEACH-LAYER-three-quarter-layered-source-v10`
- Canonical authoring application: Apple Motion 6.3
- Status: ready for an isolated native-Motion canary; not a rig approval record

This note does not promote a rig, approve either provisional leg-root pivot, or change the approved source package. Human approval remains mandatory for the native rig and every reusable motion.

## Audit result

The installed production applications are:

- Apple Motion 6.3
- Final Cut Pro 11.0.1
- Compressor 5.3
- macOS 26.5.2

No Peach `.motn`, `.moef`, `.moti`, or `.motr` project exists in the animation workspace. No user Motion template was found under the user Movies templates location. The machine contains Apple-installed sample Motion projects under `/Library/Application Support/Final Cut Pro/Templates.localized`; they confirm that Motion projects are XML-based and that Apple sample projects use native `Widget` and `Image Mask` nodes. Their XML is useful for inspection, but hand-editing undocumented Motion project XML is not an approved construction method.

GUI automation remains permission-gated. The existing environment audit records Accessibility UI automation as disabled, and a fresh read-only automation check did not establish a trusted UI-control path. The native project therefore requires either:

1. a human-controlled Motion session; or
2. explicit approval to enable the required macOS Accessibility control for the available automation host.

No approved asset or shared manifest was changed during this audit.

## Source-ingest decision

Import the 29 approved full-canvas RGBA PNG files directly into a standard Motion Composition. Do not make a PSD derivative the canonical ingest route.

The source package already defines the PNG files as 1254 × 1254, 8-bit RGBA with embedded sRGB and proves a zero-visible-pixel neutral recomposite against the approved target. Apple documents that Motion can import multiple still-image files simultaneously and automatically recognizes an image file's alpha channel. After import, inspect Alpha Type in the Media inspector; use the detected mode unless edge fringing proves it incorrect.

Important import control: the files are sequentially numbered, so ensure **Image Sequence is off**. Each PNG must become a separate still layer.

Official references:

- [Import media into Motion](https://support.apple.com/en-ie/guide/motion/motn38c97503/mac)
- [Alpha channels in Motion](https://support.apple.com/en-ca/guide/motion/motn125277a3/mac)
- [Source media controls in Motion](https://support.apple.com/en-ca/guide/motion/motnd8bd71de/mac)

## Project settings that must be fixed before canonical creation

Create a native canary before the complete rig. Use:

- 1254 × 1254
- square pixels
- progressive scan
- transparent background
- Standard Gamut SDR
- source color treatment that preserves the embedded sRGB appearance

Peter Brown fixed **30 fps** as the canonical phase-one frame rate on
4 August 2026. Use 30 fps throughout the rig, reusable motions, expression
tests, templates, review renders and phase-one delivery presets. This timing
decision does not approve any rig mechanic or rendered output.

## Neutral-stack acceptance test

Before adding any rig mechanics:

1. Import all 29 PNGs as separate stills.
2. Preserve the manifest's back-to-front order.
3. Confirm every layer occupies the same 1254 × 1254 canvas and lands at the common neutral origin.
4. Lock the clean body/shading layer, face-field texture layer, and left-shoe brand layer against accidental editing.
5. Export one full-resolution transparent neutral PNG.
6. Compare it against `PEACH-LAYER-three-quarter-layered-source-v10-neutral-recomposite.png`.

Acceptance is zero differing visible pixels. Any mismatch stops the rig build until layer order, alpha interpretation, color handling, or positioning is corrected.

## Native hierarchy

Use a standard Motion Composition first. Build Final Cut title/effect/generator templates only after the rig mechanics and published controls are stable.

Proposed top-level structure, back to front:

```text
PEACH-3Q-ROOT
├── REAR-FOLIAGE
│   ├── LEAF-A-PIVOT
│   ├── LEAF-B-PIVOT
│   └── STEM-PIVOT
├── REAR-LIMBS
│   ├── ANAT-R-ARM-CHAIN
│   ├── ANAT-L-ARM-CHAIN
│   ├── ANAT-R-LEG-CHAIN
│   └── ANAT-L-LEG-CHAIN
├── PELVIS-ROOT-COVERS
│   ├── ANAT-R-LEG-ROOT-COVER
│   └── ANAT-L-LEG-ROOT-COVER
├── SHORTS
├── BODY-AND-SHADING-LOCKED
├── FACE-FIELD-AND-FACE-CONTROLS
└── FOREGROUND-END-EFFECTORS
    ├── ANAT-R-GLOVE
    ├── ANAT-L-GLOVE
    ├── ANAT-R-SHOE-BLANK
    └── ANAT-L-SHOE-ART-WITH-LOCKED-BRAND
```

Arms and legs must remain behind the body, while gloves and shoes remain in front. Because one nested limb group cannot straddle the body in z-order, keep the glove and shoe groups in the foreground and attach each to a lower-limb endpoint reference object with Match Move. Apple documents that cross-group Link-position relationships can introduce coordinate offsets and suggests a reference object plus Match Move for cross-group transforms. Wire these relationships only after the final group topology is established; moving linked objects between groups later can break the result.

The left shoe artwork and `EVOLVED` brand remain a single rigid foreground end-effector. Do not publish an independent brand transform. Do not use negative X scale or horizontal flipping anywhere.

Official reference:

- [Link behavior in Motion](https://support.apple.com/guide/motion/link-behavior-motn13745d42/mac)

## Pivot-coordinate canary

The source coordinates use a top-left origin. A full-canvas Motion layer is centered at source coordinate `(627, 627)`. For a provisional source pivot `(px, py)`, the expected local Motion anchor offset is:

```text
x = px - 627
y = 627 - py
```

Changing an anchor can shift the visible layer relative to its Position, so do not apply this conversion to all limbs at once. Prove it with one duplicated upper-leg layer:

1. record the neutral Position and Anchor values;
2. set the converted anchor;
3. compensate Position until the neutral render is pixel-identical;
4. render `0°`, `+12°`, and `-12°`;
5. retain the numeric convention only if the pivot behaves as expected.

The provisional source pivots are:

| Control | Source pivot |
|---|---:|
| Root | `(642, 1075)` |
| Body | `(644, 440)` |
| Stem | `(642, 230)` |
| Leaf A | `(614, 226)` |
| Leaf B | `(670, 226)` |
| Anatomical-right arm root | `(469, 583)` |
| Anatomical-right arm bend | `(460, 638)` |
| Anatomical-left arm root | `(796, 565)` |
| Anatomical-left arm bend | `(812, 636)` |
| Anatomical-right leg root candidate | `(582, 680)` |
| Anatomical-right leg bend | `(582, 810)` |
| Anatomical-left leg root candidate | `(678, 680)` |
| Anatomical-left leg bend | `(706, 811)` |

These remain provisional until the native rig stress test and human visual review.

Official references:

- [Properties Inspector controls in Motion](https://support.apple.com/guide/motion/motna5015809/mac)
- [Adjust an anchor point in Motion](https://support.apple.com/guide/motion/motnbb630c00/mac)

## Required leg-root cover

The v10 articulation stress test proves that rotating either upper leg outward by 12 degrees exposes a background wedge at the shorts opening. Resolve this in Motion before rig approval with fixed source-derived cover layers.

### Construction

For each side:

1. Duplicate the approved upper-leg PNG layer.
2. Leave the duplicate fixed in pelvis/body space; it follows global and body translation but not thigh rotation.
3. Draw a tight Bezier mask directly on the duplicate, retaining only the root/socket pixels hidden under and immediately below the shorts opening.
4. Place the masked duplicate above the rotating upper-leg chain but below `20-SHORTS` and `30-PEACH-BODY-AND-SHADING-LOCKED`.
5. Keep the mask fully inside approved leg pixels and allow generous overlap beneath the opaque shorts.

Starting mask-fit regions in source pixels:

| Cover | Approved source layer | Initial fit region |
|---|---|---:|
| Anatomical-right root cover | `07-14-ANAT-R-LEG-UPPER.png` | x `530–625`, y `674–749` |
| Anatomical-left root cover | `09-16-ANAT-L-LEG-UPPER.png` | x `647–742`, y `674–749` |

These are fit regions, not approved mask vertices. Fit the Bezier contour visually in Motion.

### Why this is the default

- The fill pixels come from the approved upper-leg art, so the cover does not invent a new flat color, texture, outline, or shading treatment.
- At neutral, the duplicate is coincident with the original and mostly occluded by the shorts. A correct mask should preserve the zero-difference neutral frame.
- Applying a mask directly to each duplicate limits rasterization scope. Apple warns that masking a 2D group rasterizes the group, which can affect resolution and quality when transformed.

Official references:

- [Intro to masks and transparency in Motion](https://support.apple.com/guide/motion/intro-to-masks-and-transparency-motn173b5dff/mac)
- [How rasterization affects shapes in Motion](https://support.apple.com/guide/motion/motne6b2ddf0/mac)

### Cover acceptance test

Render each leg separately at:

- neutral;
- `+12°` and `-12°` at the `(582, 680)` / `(678, 680)` root candidates;
- the same angles at the previously tested alternate y-coordinate `704`;
- one modest over-travel angle beyond the intended published range.

Inspect on transparent checkerboard, light background, and dark background. Pass criteria:

- no background wedge;
- no floating patch or duplicate outline;
- no texture discontinuity visible at normal review size;
- zero visible-pixel difference at neutral;
- left-shoe branding remains intact and correctly oriented;
- no horizontal flip or negative X scale.

If a static source-derived cover cannot pass, the next reversible fallback is a second, smaller masked duplicate whose rotation is linked at approximately half the thigh rotation. Do not add that complexity unless the static cover fails. A generic painted oval or solid-color socket is not the preferred fallback because it creates unapproved artwork.

## Build order after the cover passes

1. Complete one leg chain: upper leg, lower leg, root cover, endpoint reference, foreground shoe.
2. Verify the leg through its intended motion range.
3. Complete one arm chain and foreground glove attachment.
4. Mirror the architecture by anatomical side without flipping the artwork.
5. Add stem and leaf pivots.
6. Add body/root controls.
7. Add face controls and expression-state switching.
8. Add Rig widgets and publish only the controls needed by the reusable system.
9. Run transparent, light-background, dark-background, and social-frame exports.
10. Present the native rig for the mandatory human approval gate before reusable motions are promoted.

## Current blockers and next safe actions

The supported Save Current Frame path is now proven. It produced 1254 × 1254,
16-bit/color transparent RGBA sRGB exports from the ordered 29-layer stack and
the separate single-neutral Motion reference. The two exports are
byte-identical, with zero RGB or alpha differences. The earlier isolated
8-bit linear-renderer discrepancy is diagnostic-path quantization evidence
only.

1. **One full-canvas anchor compensation is verified at neutral.** The
   anatomical-right upper-leg pivot at source-canvas coordinate `(582, 680)`
   uses Motion anchor and position `(-45, -53)`. Its supported neutral export
   is byte-identical to the proven neutral.
2. **The leg-root cover contour is not yet constructed or approved.** Motion
   exposes and selects the native Bezier Mask tool, but the current synthetic
   canvas gesture did not create a mask object. The failed duplicate was
   removed, leaving the saved pivot-only canary neutral-exact. Build the static
   duplicate cover through a native canvas interaction and render the stress
   grid for visual review.
3. **Final Cut Pro 11.0.1 compatibility is not yet proven.** Treat Final Cut template publication as a later, separate canary after the Motion rig passes.

The exact next safe production action is the fixed source-derived root cover
for the proven upper-leg pivot. This does not approve the pivot, cover, rig,
motions, expressions, templates, further exports, or deployment.
