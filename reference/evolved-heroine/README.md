# Evolved Heroine Asset System

**Status:** Asset storage and deployment policy
**Last updated:** 2026-08-04

This folder is the source of truth for how Evolved Heroine assets are produced, approved, stored, and deployed. Future prompt files, construction rules, validation checklists, and agent instructions should live here.

Marketing selection, composition, channel use, derivatives, accessibility, and prohibited uses are governed by `marketing-usage-guide.md`. Reusable character motion and rigging are governed by `animation-system.md`.

## Core Principle

Every character asset has one asset ID, one approved master, and any number of clearly labelled deployment versions.

Do not treat ChatGPT conversations, Canva files, WordPress uploads, social posts, or video projects as the source of truth. They are production records or downstream uses of the approved master.

## Where Everything Lives

### Evolved workspace: production intelligence

Store the system's text-based and operational material in this workspace:

- Style guide and construction rules
- Master generation instructions
- Pose and exercise specifications
- Asset register and production status
- Validation and approval checklists
- Prompt and revision history
- Agent or command instructions
- Links to approved Drive masters and deployed versions

These files should be searchable and version-controlled. Do not rely on separate ChatGPT threads to preserve production history.

### Google Drive: approved master artwork

Store the approved, high-resolution transparent PNG files in the shared Evolved Heroine Drive library. Drive is the master artwork archive and the human-friendly distribution library for Canva, Adobe, video editing, staff, and contractors.

Recommended Drive structure:

```text
Evolved Heroine Assets/
├── 01 Approved Masters/
├── 02 Awaiting Approval/
├── 03 Superseded/
├── 04 Website Versions/
└── 05 Video and Social Versions/
```

The current shared working folder is:

<https://drive.google.com/drive/folders/1N6PXBx1tbGdTsc3750mf_zIti6Ze9Tj8>

An approved master must never be overwritten silently. Preserve the previous local master in the dated local `outputs/evolved-heroine/superseded/` archive before promotion. When an existing approved Drive asset is being corrected, replace that Drive file in place only after Peter Brown approves the candidate; preserve the Drive file ID, category folder, filename convention, and spreadsheet link, then verify all four. Use Drive `03 Superseded` when the previous Drive binary must also remain independently browsable.

### Websites and publishing platforms: deployment copies

Never serve production website images directly from Google Drive. Upload an optimised derivative to WordPress or an approved image delivery service.

Canva, video projects, social platforms, and campaign files may use copies of the approved master. They must not become alternative master files.

## Asset Lifecycle

1. Select an incomplete asset ID from the register.
2. Create or update its local pose specification and generation prompt.
3. Generate the high-resolution transparent artwork.
4. Validate it against the current style guide, construction sheet, pose rules, equipment rules, and file requirements.
5. Save it to Drive under `02 Awaiting Approval`.
6. Obtain human approval before designating it as a master.
7. Move the approved file to `01 Approved Masters` and record its Drive link in the local register.
8. Create only the deployment derivatives required for the intended channels.
9. Record deployed locations in the local asset register.

Bulk production must not begin until one pilot asset from that category has passed this lifecycle end to end. A pilot approval locks the category's interpretation of pose, apparel, and allowed props; it does not create a new character-style authority.

## Required File Types

### Approved master

- PNG
- High resolution
- Transparent background
- sRGB colour profile
- Entire character visible unless the asset specification explicitly requires a crop
- No unintended shadow, backdrop, border, badge, or text

The approved transparent PNG is intended for design and video use. Preserve it at full quality.

The file's internal format must match its extension and MIME type. A HEIF or HEIC image renamed with a `.png` extension is not a valid PNG master.

If a generated asset is HEIF or HEIC, convert it to a true RGBA PNG, confirm that transparency survives, visually compare it with the source, and only then replace the incorrectly labelled Drive copy. Preserve the original in `03 Superseded` until the converted file has been verified.

### Website derivative

Create an appropriately sized WebP or AVIF version for website delivery. Retain a PNG derivative only when its transparency or visual quality is materially better for the use case.

Website files should be sized for their displayed dimensions rather than uploading the full-resolution master by default.

### Social and video derivatives

Create channel-specific copies from the approved master. Backgrounds, crops, animation, text, and effects belong in these derivatives, not in the master file.

## Naming and Identity Rules

Use the asset ID from the master register as the permanent identity. Until the spreadsheet and Pose Guide ID systems are reconciled, preserve both identifiers as metadata and do not silently renumber existing assets.

Recommended filenames:

```text
CHR007-kneeling-master-v1.png
CHR007-kneeling-web-800w-v1.webp
CHR007-kneeling-instagram-story-v1.png
CHR007-kneeling-video-4k-v1.png
```

Filenames should contain:

1. Permanent asset ID
2. Short descriptive slug
3. Intended use
4. Version number

## Approval and Quality Rules

An asset is not approved merely because an image has been generated or saved. It becomes an approved master only after it passes the documented validation checklist and receives human approval.

At minimum, confirm:

- The heroine is recognisable and consistent with the official construction sheet
- Body shape and proportions are correct
- The peach remains the complete body rather than becoming a head attached to a human torso
- Limbs remain simple cartoon tubes even when extended for exercise mechanics
- Face, leaves, stem, gloves, shoes, and colours are consistent
- Shoe branding follows the locked left-shoe placement rule
- Approved athletic bottoms are present whenever the pose exposes the upper-leg or hip transition
- Pose or exercise mechanics are accurate
- Equipment does not intersect the body incorrectly
- The silhouette remains readable
- The background is transparent
- There are no unrequested words, badges, borders, or scenery
- The asset ID and filename are correct

### Mandatory technical gate

Unless an asset brief explicitly records a different approved canvas requirement, every master candidate must pass all of the following before visual approval:

- Exactly 1254 × 1254 pixels
- True PNG with RGBA colour mode
- Alpha channel contains both fully transparent and fully opaque pixels
- All four corner pixels are fully transparent
- No chroma-key blue or green remnants
- No one-pixel edge debris, halos, accidental floor line, or clipped artwork
- Entire intended character and allowed equipment fit within the canvas

Record the technical result separately from the human visual decision. Technical compliance cannot approve an off-model image, and visual appeal cannot waive a failed file check.

When a generated result conflicts with an official rule, do not approve it based on visual appeal alone. Record the conflict and resolve the source rule before continuing production.

## Approved Athletic Bottoms

Lower-body apparel is an approved variable. The heroine may wear either:

- Fitted black athletic shorts matching FUN003, FND001, FND002, and FND005 Lat Pulldown
- Fitted black full-length tights matching the established assets that use tights

Use the official dark palette: black `#383536` as the base, with existing dark plum outline and shading treatment. Preserve the simple vintage athletic-mascot finish used across the approved references.

Choose shorts or tights according to pose clarity, exercise mechanics, and silhouette. This variation is intentional and does not represent character drift.

Apparel is mandatory whenever a pose would otherwise create an uninterrupted peach-coloured body-to-upper-leg shape that could read as nudity or human anatomy. Never depict a pelvis, groin, anatomical thighs, bodysuit effect, or skin-tight peach-coloured lower torso.

For `CHR007 — Kneeling`, fitted black athletic shorts are required. The shorts must clearly separate the peach body from the simple cartoon legs while leaving both knees, lower legs, and pink sneakers mechanically readable.

## Body Architecture and Limb Rules

The peach is always the heroine's complete body and must dominate the silhouette. It is simultaneously her head and torso; never place it on top of a separate human body.

### Locked Peach Silhouette, Volume, and Colour

`FND002 — Squat` is the primary construction reference for the peach body's contour and lower taper. `FND004 — Overhead Press` is the primary authority for vintage value separation, hard cel-shadow shapes, highlight placement, and ink accents. `FND001 — Deadlift` supports both. These traits apply across every category, including non-exercise poses.

- The upper third is full and rounded, with two readable upper lobes and a visible top cleft around the stem.
- Below the widest point, both sides taper inward toward the lower third. Do not draw the body as a circle, sphere, ball, or uniformly round orange mascot.
- The underside finishes in two soft lower lobes that converge toward a distinct pointed lower centre. This may suggest the natural paired contour of a peach, but must never become human buttocks, a pelvis, hips, or anatomical anatomy.
- Preserve definition through the midsection and lower body with the full FND004 value range: a warm peach base, a clearly separated coral-red mid-shadow, an almost black deep-plum perimeter and underside shadow, and a light cream highlight across the viewer-left and upper surface.
- The deep-plum shadow must occupy a readable graphic area along the lower and viewer-right perimeter. It cannot be reduced to the outline alone or replaced by a soft orange gradient.
- Include a small number of deliberate tapered dark-plum ink slashes within the coral shadow, matching FND004's vintage carved-print accents. Keep them sparse and directional.
- Use the warm coral-peach palette established by FND001 and FND002. Reject flat orange colouring, pale plastic peach, glossy gradients, or airbrushed volume.
- Model the form with two-to-three hard-edged cel tones and restrained vintage ink texture. The definition must come from graphic silhouette and cel-shadow shapes, not 3D rendering.
- Athletic shorts remain a shallow garment band around the peach's lower edge. They must not flatten the pointed underside into a broad horizontal curve or manufacture a human waist or hips.

Every generation prompt and visual QA pass must explicitly test the upper fullness, lower taper, paired lower lobes, pointed centre, midsection definition, FND004-style cream highlight, coral mid-shadow, deep-plum perimeter and underside shadow, sparse carved-print ink slashes, and Foundation Strength colour balance.

Never add or imply:

- A separate chest or abdomen
- A narrow human waist
- Human hips or pelvis
- A groin shape
- Anatomical thighs, calves, shoulders, or muscular contours
- A bodysuit or leotard construction that makes the peach read as a head

Arms and legs attach directly to the sides or lower edge of the peach. They remain simple, rounded cartoon tubes with the approved gloves and sneakers at their ends.

Legs are allowed and necessary for exercise poses. They may bend, extend, shorten, rotate, or foreshorten enough to communicate correct exercise mechanics, provided they remain simple mascot limbs and the peach continues to dominate the character's silhouette.

Athletic shorts must appear as a shallow garment around the lower edge of the peach, not as high-waisted human briefs. Tights may cover the tube legs but must not introduce a waist, hips, pelvis, or anatomical leg contours.

Reject any output that reads as a peach head attached to a human, even if its pose mechanics are otherwise correct.

For `CHR007 — Kneeling`, use a compact three-quarter view. The peach body sits directly above the bent tube legs, the black shorts remain a shallow visible band, and both pink sneakers fold naturally behind or beside the character without creating anatomical thighs or hips.

## Locked Shoe Branding

The word `Evolved` appears on the outward-facing side panel of the heroine's anatomical left shoe only. In a front-facing pose, this will usually be the shoe on the viewer's right.

This placement is fixed across every asset:

- Exact word: `Evolved`, with a capital `E` and lowercase remaining letters
- Place it only on the lateral, outward-facing side panel of the left sneaker
- Never place it on the right sneaker
- Never duplicate it across both shoes
- Never move it to whichever shoe happens to face the viewer
- If the outside panel of the left shoe is hidden by the pose, leave the branding unseen rather than relocating it
- Do not add other words, initials, pseudo-text, or shoe logos

Every generation prompt must state this rule explicitly. Every visual QA pass must identify the anatomical left shoe and reject the asset if the word changes feet, appears twice, is misspelled, or moves to another shoe surface.

## Approved Visual Calibration Set

The following existing assets were selected by Peter Brown on 2026-07-17 as the most accurate examples of how the Evolved Heroine should look:

| Asset ID | Asset |
| --- | --- |
| CHR002 | Standing Relaxed |
| CHR005 | Walking |
| FND001 | Deadlift |
| FND004 | Overhead Press |
| FUN003 | Single Arm Dumbbell Overhead Press |
| FITN001 | Running |
| FITN004 | Pistol Squat |
| FITN007 | ATG Split Squat |

Use this set collectively to calibrate character identity, proportions, facial treatment, palette, line work, and acceptable movement deformation. No single pose overrides the Style Guide or Construction Sheet on its own; where the eight references disagree, record the variation and resolve it before turning that trait into an automated validation rule.

## Locked Original Rendering Style

Every new or corrected master must use the original 2D vintage athletic-mascot treatment established by the Approved Visual Calibration Set:

- Hand-inked 2D sports-mascot illustration
- Heavy dark-plum outer contours and internal linework
- Simplified graphic shapes and flat cel colours
- Limited two-to-three-tone cel shading
- Small, hard-edged graphic highlights
- Subtle vintage screen-print or ink texture
- Restrained facial and eye proportions matching the original references

Texture is secondary to value separation. Grain or speckling must never substitute for the large hard-edged cream, peach, coral, and deep-plum graphic regions that make the original character pop.

Do not use 3D, Pixar-like or Disney-like animation, CGI, clay, plush, vinyl-toy or glossy-plastic rendering. Reject soft studio lighting, gradients, volumetric shading, ambient occlusion, inflated rounded forms, photoreal materials, cinematic polish, oversized glossy eyes, or airbrushed surfaces.

## Reference Hierarchy and Anti-Drift Rules

Only the eight Approved Visual Calibration Set masters may define character identity and rendering style. A newly generated or corrected descendant must never become a style reference merely because it is newer or has been approved for its pose.

A newer approved asset, including CUT001 v3 and the final v3 correction batches, may be used as an implementation benchmark for checking whether the locked rules were applied consistently. It may also be used as a pose-only, expression-only, apparel-only, or equipment-only reference when necessary. It never replaces or joins the eight original style authorities.

Every supplied reference must be assigned exactly one or more explicit roles:

- **Target/pose:** composition, gesture, exercise mechanics, or expression to preserve
- **Identity/style:** only members of the eight Approved Visual Calibration Set
- **Construction/value:** the named original masters that demonstrate silhouette or vintage shade separation
- **Apparel:** approved shorts, tights, gloves, or shoes only
- **Equipment/prop:** object geometry and safe character interaction only

Ignore every feature outside a reference's assigned role. In particular, do not inherit an unrequested barbell, dumbbell, bench, floor, background, clothing item, pose, lighting treatment, or text from another reference.

Every generation prompt must identify:

1. The edit target, if an existing pose is being corrected
2. The original calibration masters used as identity and style references
3. Any pose-only or equipment-only references
4. The asset brief's exact allowed props and forbidden props
5. The locked rendering rules and prohibited drift characteristics

If an object is not explicitly allowed by the asset brief, it is forbidden. A reference image containing equipment is never permission to reproduce that equipment.

Visual QA must compare the candidate directly with the original calibration masters before approval. An anatomically correct or appealing image still fails if it introduces a more refined, glossy, dimensional, or animated-film-like finish.

Use `final-generation-prompt-template.md` for every new or corrected candidate. The remaining planned production queue and its per-asset pose/prop briefs are controlled by `remaining-42-production-register.md`.

## Style-Correction Versioning

Never overwrite a drifted approved master. Create a new version, preserve the prior version as superseded, and update the active Drive, prompt, local record, and spreadsheet links only after Peter Brown approves the correction.

## System of Record

The local asset register controls production status, prompt history, validation, versions, and deployment links. Google Drive controls the approved master binary files.

The Google Sheet may remain as a human-friendly dashboard or mirror. If both registers are maintained, the agent must update them together and report any mismatch rather than guessing which entry is correct.

## Future Automation Rule

The Evolved Heroine production agent should automate prompt creation, image generation, file naming, validation, derivative creation, Drive filing, and register updates. Human approval remains mandatory before a new or revised image enters `01 Approved Masters`.
