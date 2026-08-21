# Evolved Heroine Final Generation Prompt Template

**Status:** Mandatory production template  
**Last updated:** 2026-08-03

Use this template for every new or corrected Evolved Heroine master. Complete every bracketed field from the asset's approved pose brief before generation. Do not improvise additional props, scenery, apparel, branding, or anatomy.

## Reference Roles

Attach only the minimum references needed and label each one in the prompt.

| Role | Permitted source |
| --- | --- |
| Target / pose | The asset being corrected, or one clearly named pose-only reference |
| Identity / style | Only the eight original Approved Visual Calibration Set masters in `README.md` |
| Construction | FND002 primary; FND001 supporting |
| Vintage value and shading | FND004 primary; FND001 and FUN003 supporting |
| Apparel | A named approved original showing the required shorts or tights |
| Equipment / prop | A named reference used only for object shape and safe interaction |
| Implementation benchmark | CUT001 v3 or an approved final v3 asset, used only to check faithful application of the original rules |

Ignore all content outside each reference's assigned role. Never transfer a prop, background, pose, lighting treatment, text element, or clothing item merely because it appears in a supplied reference.

## Copy-Paste Generation Prompt

```text
Create one production-ready Evolved Heroine transparent PNG master.

ASSET
- Asset ID: [ASSET ID]
- Category: [CATEGORY]
- Asset name: [ASSET NAME]
- Pose and visual intent: [PASTE THE APPROVED POSE BRIEF]
- Expression: [EXPRESSION]
- Apparel: [BLACK SHORTS / BLACK TIGHTS / OTHER EXPLICITLY APPROVED APPAREL]
- Allowed props only: [EXACT LIST, OR NONE]
- Forbidden props: [EXACT LIST, INCLUDING COMMON REFERENCE-CONTAMINATION RISKS]

REFERENCE ROLES
- Target/pose reference: [FILE OR NONE]. Use only for [POSE / COMPOSITION / EXPRESSION].
- Identity/style references: [SELECT FROM THE ORIGINAL EIGHT ONLY]. Use only for character identity, proportions, face, linework, palette, and original 2D vintage athletic-mascot rendering.
- Construction reference: FND002. Use for full upper lobes, clear top cleft, inward lower taper, paired lower lobes, and pointed lower centre.
- Vintage value reference: FND004. Use for the hard cream highlight, warm peach base, coral-red mid-shadow, deep-plum perimeter and underside shadow, and sparse carved-print ink slashes.
- Supporting original reference: [FND001 / FUN003 / OTHER ORIGINAL CALIBRATION MASTER]. Use only for [NAMED ROLE].
- Equipment/prop reference: [FILE OR NONE]. Use only for object geometry and safe hand/body interaction.
- Implementation benchmark: [CUT001 V3 OR APPROVED V3 ASSET OR NONE]. It is not a style authority and must not override the original references.

LOCKED CHARACTER CONSTRUCTION
- Peach is the complete head-and-body silhouette, never a peach head on a human torso.
- Preserve two full rounded upper lobes, the stem cleft, an inward taper below the widest point, two soft lower fruit lobes, and a distinct pointed lower centre.
- Preserve visible midsection definition through hard-edged vintage colour regions, not human anatomy.
- Arms and legs are simple rounded mascot tubes attached directly to the peach.
- No human chest, abdomen, waist, hips, pelvis, groin, thighs, calves, shoulders, or muscular anatomy.
- Approved athletic bottoms form a shallow dark garment band and must clearly separate peach body from legs.

LOCKED ORIGINAL RENDERING
- Hand-inked flat 2D vintage athletic mascot.
- Heavy deep-plum contours and internal linework.
- Two-to-three hard-edged cel tones with cream, warm peach, coral-red, and deep-plum value separation.
- Readable deep-plum shadow area on the lower and viewer-right perimeter.
- Small hard cream highlights and sparse directional carved-print ink slashes.
- Restrained original facial proportions and eye treatment.
- No 3D, Pixar-like, Disney-like, CGI, glossy plastic, plush, clay, airbrushed, volumetric, gradient-heavy, or cinematic rendering.
- No soft ambient-occlusion modelling, oversized glossy eyes, inflated round body, or uniformly orange colouring.

POSE, PROP, AND BRAND SAFETY
- Preserve the approved pose mechanics and a clear readable silhouette.
- Include only the allowed props. If a prop is not explicitly allowed above, omit it.
- Equipment must remain fully visible where required and must never pass through, merge with, or disappear behind the body incorrectly.
- The exact word “Evolved” may appear only on the outward-facing side panel of the anatomical left shoe. If that panel is hidden, omit the word. Never move it, duplicate it, misspell it, or add pseudo-text.
- No other writing, logo, badge, border, scenery, floor, cast shadow, or backdrop.

OUTPUT
- One isolated full-character composition on a transparent background.
- Exactly 1254 × 1254 pixels.
- True RGBA PNG with fully transparent corners and no chroma fringe or edge debris.
- Keep all intended character parts and allowed equipment inside the canvas.
```

## Mandatory Review Gates

1. **Brief gate:** ID, pose, expression, apparel, allowed props, and forbidden props match the local brief.
2. **Reference gate:** every reference has a declared role; only original calibration masters control style.
3. **Construction gate:** peach silhouette, pointed lower centre, tube limbs, and non-human anatomy pass.
4. **Vintage gate:** hard cream/peach/coral/deep-plum regions and restrained ink texture match the originals.
5. **Pose and prop gate:** mechanics read correctly; nothing intersects, disappears, or migrates from another reference.
6. **Brand gate:** `Evolved` is correct and only on the anatomical left shoe's outside panel when visible.
7. **Technical gate:** 1254 × 1254 true RGBA PNG; usable alpha; four transparent corners; no chroma remnants, halo, clipping, floor, or edge debris.
8. **Human gate:** Peter Brown explicitly approves the visual candidate before master promotion or Drive replacement.

## Batch Rule

Generate and approve one pilot from each previously unbuilt category before producing the rest of that category. If the pilot exposes a new interpretation issue, update the category briefs first; do not silently solve it differently across the batch.
