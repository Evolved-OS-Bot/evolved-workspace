# Evolved Heroine Style-Correction Batch

**Date:** 23 July 2026  
**Status:** PNG batch approved and promoted; Drive prompt upload pending separate explicit authorisation  
**Purpose:** Correct the glossy, refined 3D/Pixar-like drift and return affected PNGs to the original 2D vintage athletic-mascot style.

## Outcome

The FRD001 pilot was approved and promoted separately. Peter Brown approved the remaining 33 corrected PNGs on 23 July 2026:

- Character: CHR007–CHR008
- Achievement: ACH001–ACH008
- Celebration: CEL001–CEL008
- Friendly: FRD002–FRD008
- Cute: CUT001–CUT008

The full correction programme therefore covers 34 approved PNG assets including the FRD001 v2 pilot.

## Candidate Location

```text
outputs/evolved-heroine/candidates/style-correction/batch-2026-07-23/
```

Each current candidate uses the suffix `style-correction-v2-candidate.png`, except FRD008, whose corrected shoe-lock candidate is `FRD008-arms-open-welcome-style-correction-v3-candidate.png`.

The rejected FRD008 v2 is retained and explicitly labelled `rejected-wrong-shoe`; it must not be promoted.

## Review Sheets

```text
outputs/evolved-heroine/candidates/style-correction/batch-2026-07-23/review-sheets/
```

Review sheets are grouped into character, achievement, celebration, friendly, and cute categories. A separate shoe-branding sheet provides a closer comparison of wordmark spelling and placement.

## Correction Lock

All candidates were rebuilt using the original calibration set as the visual authority:

- CHR002: Standing Relaxed
- CHR005: Walking
- FND001: Deadlift
- FND004: Overhead Press
- FUN003: Single Arm Dumbbell Overhead Press
- FITN001: Running
- FITN004: Pistol Squat
- FITN007: ATG Split Squat

The correction prompt required:

- Hand-drawn 2D vintage athletic-mascot illustration
- Heavy dark-plum ink outlines
- Flat cel colours with two to three shading tones
- Hard graphic highlights and subtle rough print texture
- One complete peach fruit serving as both head and torso
- Exactly two green leaves and one short brown stem
- Cream gloves, simple tube limbs, dark shorts or tights, and pink sneakers
- No human torso, breasts, waist, hips, or realistic skin anatomy
- No 3D, CGI, Pixar-like, glossy plastic, photorealistic, or soft volumetric rendering
- Exact word `Evolved` once on the outside of the anatomical left sneaker; the other shoe blank
- Flat chroma-blue generation background followed by controlled conversion to transparent RGBA PNG

## Validation Result

Automated validation passed all 33 current candidates:

- 1254 × 1254 pixels
- RGBA PNG
- Fully transparent canvas corners
- Alpha channel spans fully transparent to fully opaque
- No candidate replaced an approved master

Direct visual review identified one initial exception: FRD008 v2 placed `Evolved` on the wrong shoe. FRD008 was regenerated as v3 and passed the placement review.

## Approval and Promotion Rule

Peter Brown approved the PNG batch on 23 July 2026. The following promotion work is complete:

1. The 33 accepted transparent PNGs were promoted to the local approved-master folder.
2. The 25 former approved local masters were preserved in `outputs/evolved-heroine/superseded/style-drift-2026-07-23/`.
3. The 25 existing Drive PNG records were archived and replaced in place with corrected v2 bytes, preserving their file IDs and spreadsheet links.
4. A new Drive `PNGs/Cute` folder was created and CUT001–CUT008 were uploaded as approved v1 masters.
5. The Cute spreadsheet asset flags and links were updated and verified.
6. All 33 local asset records were updated with approval, master version, Drive location and current PNG QA.
7. All 33 approved prompt files were prepared locally.

The Drive connector rejected upload of the 33 local prompt documents because they contain proprietary production instructions and require a separate explicit user authorisation. The 25 existing Drive prompt documents were restored to their category folders so no current spreadsheet links are broken. Cute prompt fields remain incomplete until that authorisation is given.

Next action: obtain explicit approval to upload the 33 proprietary prompt documents to Google Drive, archive the 25 superseded Drive prompts, and update all prompt links and status fields in the master spreadsheet.

## Cute Silhouette and Vintage-Shading v3 Addendum

Peter's follow-up review identified two remaining Cute-category differences: the fruit body was too round, and the tonal treatment was too flat. FND002 is the construction authority for the full upper lobes, tapered lower sides, paired lower lobes and pointed lower centre. FND004 is the primary shading authority, with FUN003 and FND001 supporting the warm palette and carved-print shadow accents.

All CUT001–CUT008 v3 PNGs were approved on 23 July 2026. They passed silhouette, vintage shading, expression, transparent-background and one-left-shoe branding review.

The eight v3 files are now the local approved masters. Earlier Cute masters are preserved in `outputs/evolved-heroine/superseded/cute-round-body-2026-07-23/`.

The existing eight Drive PNGs were replaced in place and renamed with the v3 suffix. Their Drive file IDs and spreadsheet asset links were preserved. Prompt uploads remain a separate pending authorisation.
