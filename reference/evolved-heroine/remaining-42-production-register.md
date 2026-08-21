# Evolved Heroine Remaining 42 Production Register

**Status:** Complete; all 42 approved, promoted locally, uploaded to Drive, and reconciled to the master spreadsheet  
**Last reconciled:** 2026-08-04  
**Source:** `Evolved Heroine Master Spreadsheet`, `Sheet1!A9:I131`  
**Count:** 42 assets across 9 categories

This file is the local production control for the 42 Sheet rows whose `Create Asset` and `Save Asset` fields were false on the reconciliation date. The Google Sheet remains the human-friendly dashboard. Reconcile both after every approved promotion.

All assets inherit `README.md` and `final-generation-prompt-template.md`. The eight original Approved Visual Calibration Set masters are the only identity and style authorities. CUT001 v3 and later approved v3 assets are implementation benchmarks only.

## Category Order and Pilot Gate

| Order | Category | Pilot | Remaining count | Batch rule |
| ---: | --- | --- | ---: | --- |
| 1 | Coaching | COA001 | 8 | Approve pilot before COA002–COA008 |
| 2 | Healthy Habits | HLT001 | 8 | Approve pilot before HLT002–HLT008 |
| 3 | Lifestyle | LIF001 | 8 | Approve pilot before LIF002–LIF008 |
| 4 | Seasonal | SEA001 | 4 | Approve pilot before SEA002–SEA004 |
| 5 | Gym Lifestyle | GYM001 | 4 | Approve pilot before GYM002–GYM004 |
| 6 | Adventure | ADV001 | 4 | Approve pilot before ADV002–ADV004 |
| 7 | Core | COR002 | 2 | Approve pilot before COR003 |
| 8 | Wellbeing | WEL001 | 2 | Approve pilot before WEL002 |
| 9 | Success | SUC001 | 2 | Approve pilot before SUC002 |

The order favours low-complexity, brand-useful categories first and defers the highest equipment and foreshortening risk until the style system has passed several category pilots.

On 2026-08-03 Peter Brown explicitly authorised one continuous all-category candidate-production sweep. This waived the category-by-category pause for candidate generation only. It did not waive human visual approval, master-promotion, Drive-upload, or spreadsheet-verification gates.

## 2026-08-03 Full Candidate Batch

- **Batch root:** `outputs/evolved-heroine/candidates/remaining-42/batch-2026-08-03/`
- **Review index:** `outputs/evolved-heroine/candidates/remaining-42/batch-2026-08-03/review/remaining-42-contact-sheet.png`
- **Detailed review sheets:** one labelled checkerboard sheet per category in `outputs/evolved-heroine/candidates/remaining-42/batch-2026-08-03/review/`
- **Candidate count:** 42 of 42 generated and processed to transparent PNG
- **Approval state:** Peter Brown approved all 42 assets on 2026-08-04; all are promoted as local v1 masters
- **Technical QA:** all 42 candidates pass 1254 × 1254, true RGBA, alpha 0–255, and four transparent-corner checks
- **Canvas normalisation:** nine portrait or landscape generator returns were aspect-preservingly fitted to the standard 1254 × 1254 transparent canvas without cropping
- **Drive state:** all 42 approved masters are present in their verified `PNGs` category folders; exact file IDs and links are recorded in `remaining-42-approved-drive-manifest.md`
- **Sheet state:** `Sheet1` asset rows now record `Create Asset = TRUE`, `Save Asset = TRUE`, and the exact Drive file link; prompt fields remain unchanged
- **Controlled-logo exception:** SUC002 v1 is approved with its deliberately blank flag. Any later logo-bearing revision must use the exact controlled Evolved artwork and must pass the normal new-version approval workflow.

| Category | Produced | Candidate IDs | Status |
| --- | ---: | --- | --- |
| Coaching | 8/8 | COA001–COA008 | Approved, promoted, uploaded, and Sheet-verified |
| Healthy Habits | 8/8 | HLT001–HLT008 | Approved, promoted, uploaded, and Sheet-verified |
| Lifestyle | 8/8 | LIF001–LIF008 | Approved, promoted, uploaded, and Sheet-verified |
| Seasonal | 4/4 | SEA001–SEA004 | Approved, promoted, uploaded, and Sheet-verified |
| Gym Lifestyle | 4/4 | GYM001–GYM004 | Approved, promoted, uploaded, and Sheet-verified |
| Adventure | 4/4 | ADV001–ADV004 | Approved, promoted, uploaded, and Sheet-verified |
| Core | 2/2 | COR002–COR003 | Approved, promoted, uploaded, and Sheet-verified |
| Wellbeing | 2/2 | WEL001–WEL002 | Approved, promoted, uploaded, and Sheet-verified |
| Success | 2/2 | SUC001–SUC002 | Approved, promoted, uploaded, and Sheet-verified |

## Universal Brief Rules

- **Canvas:** isolated full character, 1254 × 1254 true RGBA PNG, transparent corners, no floor or cast shadow.
- **Apparel default:** fitted black athletic shorts. Use tights only where the brief calls for them or pose readability materially benefits.
- **Prop isolation:** only the props listed as allowed for that asset may appear.
- **No reference contamination:** no inherited barbell, dumbbell, bench, clipboard, bottle, scenery, text, or clothing.
- **Character lock:** original peach silhouette, Foundation Strength vintage shade separation, tube limbs, pink sneakers, white gloves, one-left-shoe `Evolved` rule.
- **Approval state:** the entries below began `Planned`; the batch-level record and approved Drive manifest now hold the reconciled 2026-08-04 final state.

## Coaching — 8

### COA001 — Holding Clipboard — PILOT

- **Pose:** Upright three-quarter coaching stance, friendly attentive expression, one hand supporting a clipboard at chest-side height and the other relaxed.
- **Allowed props:** One plain clipboard with a blank or non-readable page.
- **Forbidden props:** Pencil, whistle, stopwatch, barbell, dumbbell, bench, readable writing, charts, desk, scenery.
- **Apparel:** Black athletic shorts.
- **Status:** Approved by Peter Brown on 2026-08-03; Coaching pilot gate passed.
- **Approved prompt:** `reference/evolved-heroine/coaching/prompts/COA001-holding-clipboard-candidate-prompt-v1.txt`
- **Approved source:** `outputs/evolved-heroine/candidates/remaining-42/batch-2026-08-03/coaching/source-magenta/COA001-holding-clipboard-source.png`
- **Approved master:** `outputs/evolved-heroine/approved/COA001-holding-clipboard-master-v1.png`
- **Rejected experiment:** `outputs/evolved-heroine/candidates/remaining-42/batch-2026-08-03/coaching/transparent/COA001-holding-clipboard-candidate-v2.png`
- **Technical QA:** Pass; 1254 × 1254 true RGBA PNG, alpha 0–255, four fully transparent corners.

### COA002 — Writing on Clipboard

- **Pose:** Upright three-quarter stance, clipboard supported securely in one hand while the other writes; eyes directed toward the page without hiding the face.
- **Allowed props:** One plain clipboard and one simple pencil.
- **Forbidden props:** Whistle, stopwatch, glasses, lab coat, barbell, readable notes, floating paper, desk, scenery.
- **Apparel:** Black athletic shorts.
- **Status:** Approved and promoted on 2026-08-04; Drive and Sheet verified.
- **Candidate:** `outputs/evolved-heroine/candidates/remaining-42/batch-2026-08-03/coaching/transparent/COA002-writing-on-clipboard-candidate-v1.png`
- **Technical QA:** Pass.

### COA003 — Holding Whistle

- **Pose:** Confident coaching stance, one gloved hand holding a visible whistle near the upper body; whistle is not in the mouth.
- **Allowed props:** One simple whistle with a short plain lanyard.
- **Forbidden props:** Clipboard, pencil, stopwatch, barbell, dumbbell, text, scoreboard, scenery.
- **Apparel:** Black athletic shorts.
- **Status:** Approved and promoted on 2026-08-04; Drive and Sheet verified.
- **Candidate:** `outputs/evolved-heroine/candidates/remaining-42/batch-2026-08-03/coaching/transparent/COA003-holding-whistle-candidate-v1.png`
- **Technical QA:** Pass.

### COA004 — Holding Stopwatch

- **Pose:** Upright attentive stance, one hand presenting a clearly readable stopwatch shape while the other supports the coaching gesture.
- **Allowed props:** One analogue-style stopwatch with no readable numbers or brand.
- **Forbidden props:** Clipboard, whistle, phone, barbell, digital text, timer numbers, scenery.
- **Apparel:** Black athletic shorts.
- **Status:** Approved and promoted on 2026-08-04; Drive and Sheet verified.
- **Candidate:** `outputs/evolved-heroine/candidates/remaining-42/batch-2026-08-03/coaching/transparent/COA004-holding-stopwatch-candidate-v1.png`
- **Technical QA:** Pass.

### COA005 — Explaining

- **Pose:** Open three-quarter stance with one palm raised in a clear teaching gesture and the other hand indicating the imagined subject; warm, confident expression.
- **Allowed props:** None.
- **Forbidden props:** Clipboard, whistle, stopwatch, pointer, board, equipment, text, scenery.
- **Apparel:** Black athletic shorts.
- **Status:** Approved and promoted on 2026-08-04; Drive and Sheet verified.
- **Candidate:** `outputs/evolved-heroine/candidates/remaining-42/batch-2026-08-03/coaching/transparent/COA005-explaining-candidate-v1.png`
- **Technical QA:** Pass.

### COA006 — Demonstrating

- **Pose:** Stable athletic stance demonstrating a simple bodyweight hinge-ready position, with clear posture and open hands; instructional rather than lifting.
- **Allowed props:** None.
- **Forbidden props:** Barbell, dumbbell, bench, clipboard, whistle, mat, text, scenery.
- **Apparel:** Black athletic shorts.
- **Status:** Approved and promoted on 2026-08-04; Drive and Sheet verified.
- **Candidate:** `outputs/evolved-heroine/candidates/remaining-42/batch-2026-08-03/coaching/transparent/COA006-demonstrating-candidate-v1.png`
- **Technical QA:** Pass.

### COA007 — Listening

- **Pose:** Relaxed attentive stance with a slight forward lean and one gloved hand cupped near the ear; sympathetic expression.
- **Allowed props:** None.
- **Forbidden props:** Phone, headphones, clipboard, whistle, equipment, speech bubbles, text, scenery.
- **Apparel:** Black athletic shorts.
- **Status:** Approved and promoted on 2026-08-04; Drive and Sheet verified.
- **Candidate:** `outputs/evolved-heroine/candidates/remaining-42/batch-2026-08-03/coaching/transparent/COA007-listening-candidate-v1.png`
- **Technical QA:** Pass.

### COA008 — Encouraging

- **Pose:** Energetic forward-facing coaching stance with one supportive fist raised and the other hand open toward the viewer; motivating smile.
- **Allowed props:** None.
- **Forbidden props:** Trophy, medal, clipboard, whistle, barbell, signs, text, scenery.
- **Apparel:** Black athletic shorts.
- **Status:** Approved and promoted on 2026-08-04; Drive and Sheet verified.
- **Candidate:** `outputs/evolved-heroine/candidates/remaining-42/batch-2026-08-03/coaching/transparent/COA008-encouraging-candidate-v1.png`
- **Technical QA:** Pass.

## Healthy Habits — 8

### HLT001 — Drinking Water — PILOT

- **Pose:** Upright relaxed stance, one hand tilting a reusable bottle toward the mouth while the face remains recognisable and unobstructed.
- **Allowed props:** One plain reusable water bottle.
- **Forbidden props:** Protein shaker, cup, straw, visible liquid spill, brand label, gym equipment, scenery.
- **Apparel:** Black athletic shorts.
- **Status:** Approved and promoted on 2026-08-04; Drive and Sheet verified.
- **Candidate:** `outputs/evolved-heroine/candidates/remaining-42/batch-2026-08-03/healthy-habits/transparent/HLT001-drinking-water-candidate-v1.png`
- **Technical QA:** Pass.

### HLT002 — Holding Apple

- **Pose:** Friendly upright stance presenting one apple in a gloved palm at chest-side height.
- **Allowed props:** One simple red or green apple with a small leaf.
- **Forbidden props:** Basket, multiple fruit, knife, plate, text, gym equipment, scenery.
- **Apparel:** Black athletic shorts.

### HLT003 — Holding Protein Shake

- **Pose:** Upright athletic stance holding one closed shaker at chest-side height with a confident smile.
- **Allowed props:** One plain protein shaker with a secure lid.
- **Forbidden props:** Water bottle, supplement tub, scoop, powder, readable branding, barbell, scenery.
- **Apparel:** Black athletic shorts.

### HLT004 — Stretching

- **Pose:** Clear standing quadriceps stretch in three-quarter view, one foot held behind by the same-side hand, free arm balancing; tube-limb mechanics remain readable.
- **Allowed props:** None.
- **Forbidden props:** Yoga mat, wall, bench, weights, towel, text, scenery.
- **Apparel:** Black full-length tights.

### HLT005 — Foam Rolling

- **Pose:** Seated three-quarter floor-level pose with one simple tube leg positioned safely over a foam roller; both hands support the body and no object intersects the peach.
- **Allowed props:** One plain cylindrical foam roller.
- **Forbidden props:** Mat, dumbbell, bench, massage gun, gym rack, text, scenery.
- **Apparel:** Black full-length tights.

### HLT006 — Sleeping

- **Pose:** Peaceful side-lying curled rest pose, eyes closed, hands together near one cheek; peach remains the full body.
- **Allowed props:** One small plain pillow.
- **Forbidden props:** Bed, blanket covering the character, nightcap, alarm clock, `Z` text, room scenery.
- **Apparel:** Black athletic shorts.

### HLT007 — Reading

- **Pose:** Comfortable seated cross-legged pose holding an open book below the face; eyes directed toward the pages.
- **Allowed props:** One plain open book with blank, non-readable pages.
- **Forbidden props:** Glasses, chair, desk, coffee, readable text, bookshelf, scenery.
- **Apparel:** Black athletic shorts.

### HLT008 — Holding a Heart

- **Pose:** Warm front-facing stance holding one simple heart shape centred in front of the lower chest/body without obscuring the face.
- **Allowed props:** One plain pink or red heart symbol.
- **Forbidden props:** Anatomical heart, multiple hearts, sign, words, medical equipment, scenery.
- **Apparel:** Black athletic shorts.

## Lifestyle — 8

### LIF001 — Holding Phone — PILOT

- **Pose:** Casual upright three-quarter stance holding one smartphone at comfortable chest-side height and looking toward it.
- **Allowed props:** One plain smartphone with an unlit or abstract screen.
- **Forbidden props:** Selfie stick, headphones, readable interface, notifications, coffee, bags, scenery.
- **Apparel:** Black athletic shorts.

### LIF002 — Taking a Selfie

- **Pose:** Energetic three-quarter pose with one arm extended holding a phone slightly above eye level, face turned toward the camera, free hand giving a small wave.
- **Allowed props:** One plain smartphone.
- **Forbidden props:** Selfie stick, second phone, ring light, readable interface, mirror, scenery.
- **Apparel:** Black athletic shorts.

### LIF003 — Holding Coffee

- **Pose:** Relaxed upright stance cradling one takeaway cup in a gloved hand away from the face.
- **Allowed props:** One plain lidded takeaway cup with no logo.
- **Forbidden props:** Saucer, kettle, table, phone, readable label, visible spill or steam text, scenery.
- **Apparel:** Black athletic shorts.

### LIF004 — Holding Shopping Bags

- **Pose:** Cheerful walking or standing pose carrying a small balanced set of bags at the sides; hands and shoes remain visible.
- **Allowed props:** Two or three plain shopping bags with simple handles.
- **Forbidden props:** Brand logos, readable text, shopping trolley, phone, street or store scenery.
- **Apparel:** Black athletic shorts.

### LIF005 — Holding Gym Bag

- **Pose:** Confident walking three-quarter pose carrying one compact duffel by its handles at the side, without obscuring the legs.
- **Allowed props:** One plain gym duffel.
- **Forbidden props:** Loose equipment, towel, drink bottle, brand text, locker-room scenery.
- **Apparel:** Black athletic shorts.

### LIF006 — Holding Flowers

- **Pose:** Warm upright pose holding a modest bouquet to one side of the body so the peach silhouette and face remain visible.
- **Allowed props:** One small mixed-flower bouquet with a simple wrap.
- **Forbidden props:** Vase, card, readable text, oversized bouquet, garden scenery.
- **Apparel:** Black athletic shorts.

### LIF007 — Holding Present

- **Pose:** Front-facing celebratory stance holding one small gift box at mid-body height without hiding the pointed peach base.
- **Allowed props:** One plain wrapped box with a simple ribbon.
- **Forbidden props:** Multiple gifts, readable tag, birthday cake, confetti, Christmas hat, scenery.
- **Apparel:** Black athletic shorts.

### LIF008 — Reading a Map

- **Pose:** Curious upright three-quarter stance holding one folded map open below the face; gaze directed toward it.
- **Allowed props:** One simple folded paper map with abstract lines only.
- **Forbidden props:** Readable place names, compass, backpack, phone, road signs, landscape scenery.
- **Apparel:** Black athletic shorts.

## Seasonal — 4

### SEA001 — Christmas Hat — PILOT

- **Pose:** Friendly neutral hero stance wearing a correctly fitted festive hat while preserving the stem and at least one leaf as readable character features.
- **Allowed props:** One red-and-cream Santa-style hat.
- **Forbidden props:** Gifts, tree, ornaments, snow, readable text, extra costume, scenery.
- **Apparel:** Black athletic shorts.

### SEA002 — Birthday Cake

- **Pose:** Cheerful upright stance presenting a small cake on both open palms at chest-side height; face and peach silhouette remain clear.
- **Allowed props:** One small plain birthday cake on a simple plate with one unlit candle.
- **Forbidden props:** Flames, knife, readable age, balloons, presents, confetti, table, scenery.
- **Apparel:** Black athletic shorts.

### SEA003 — Halloween Pumpkin

- **Pose:** Playful upright pose holding one small carved pumpkin at the side, with a friendly expression rather than horror styling.
- **Allowed props:** One small orange jack-o'-lantern.
- **Forbidden props:** Weapons, blood, gore, witch costume, bats, smoke, readable text, haunted scenery.
- **Apparel:** Black athletic shorts.

### SEA004 — Easter Egg

- **Pose:** Cheerful upright stance holding one large decorated egg in both hands to one side of the pointed lower body.
- **Allowed props:** One patterned Easter egg with simple non-text decoration.
- **Forbidden props:** Basket, rabbit costume, multiple eggs, readable text, grass or scenery.
- **Apparel:** Black athletic shorts.

## Gym Lifestyle — 4

### GYM001 — Holding Dumbbell — PILOT

- **Pose:** Confident upright three-quarter stance holding one dumbbell securely at the side in a neutral grip; not performing a curl or press.
- **Allowed props:** One compact gym dumbbell.
- **Forbidden props:** Second dumbbell, barbell, bench, rack, plates, floor shadow, scenery.
- **Apparel:** Black athletic shorts.

### GYM002 — Carrying Barbell Across Shoulders

- **Pose:** Stable front or slight three-quarter standing carry with a straight bar resting safely across the upper rear silhouette, both hands evenly spaced; bar remains behind the peach and never passes through it.
- **Allowed props:** One unloaded straight barbell.
- **Forbidden props:** Weight plates, squat rack, bench, collars, floor shadow, scenery.
- **Apparel:** Black full-length tights.

### GYM003 — Resting on Bench

- **Pose:** Relaxed seated three-quarter pose on the end of a flat bench, slight forward lean, forearms resting on simple tube legs; both shoes visible.
- **Allowed props:** One plain flat gym bench.
- **Forbidden props:** Barbell, dumbbells, rack, towel, bottle, floor shadow, scenery.
- **Apparel:** Black athletic shorts.

### GYM004 — Chalking Hands

- **Pose:** Focused standing stance rubbing gloved hands together at chest-side height, with a very restrained chalk cue.
- **Allowed props:** A small controlled white chalk dust accent around the hands.
- **Forbidden props:** Chalk bowl, bucket, barbell, dumbbell, large dust cloud, floor debris, text, scenery.
- **Apparel:** Black athletic shorts.

## Adventure — 4

### ADV001 — Hiking — PILOT

- **Pose:** Energetic three-quarter walking stride with one foot forward and one compact pack carried naturally; silhouette remains clean.
- **Allowed props:** One small plain backpack.
- **Forbidden props:** Trekking poles, map, tent, mountain, trail, trees, readable badges, scenery.
- **Apparel:** Black full-length tights.

### ADV002 — Camping

- **Pose:** Cheerful standing pose holding one neatly rolled sleeping mat at the side, suggesting camping without an environment.
- **Allowed props:** One plain rolled sleeping mat with simple straps.
- **Forbidden props:** Tent, fire, axe, backpack, lantern, landscape, readable text, scenery.
- **Apparel:** Black full-length tights.

### ADV003 — Swimming

- **Pose:** Dynamic side-view freestyle swimming action with one arm extended and one recovering, simple tube legs trailing; character is isolated with no water plane.
- **Allowed props:** A few small flat graphic splash accents immediately around the limbs.
- **Forbidden props:** Pool, lane rope, goggles, swim cap, float, horizon, large water background, text.
- **Apparel:** Approved fitted black athletic shorts; no human swimsuit or bodysuit construction.

### ADV004 — Cycling

- **Pose:** Clear three-quarter cycling action on a simple bicycle, hands on handlebars and both feet aligned safely with pedals; peach remains dominant.
- **Allowed props:** One simplified bicycle and one plain fitted cycling helmet.
- **Forbidden props:** Road, mountains, traffic, bottle, basket, readable bike branding, scenery.
- **Apparel:** Black full-length tights.

## Core — 2

### COR002 — Side Plank — PILOT

- **Pose:** Mechanically correct side plank in profile, lower forearm planted beneath the shoulder attachment, peach body held as one stable diagonal mass, simple stacked tube legs and upper arm raised.
- **Allowed props:** None.
- **Forbidden props:** Mat, dumbbell, bench, floor line, text, scenery.
- **Apparel:** Black full-length tights.

### COR003 — Dead Bug

- **Pose:** Supine three-quarter dead-bug position with opposite arm and leg extended and the other pair bent; clear contralateral mechanics, tube limbs, and unobstructed peach body.
- **Allowed props:** None.
- **Forbidden props:** Mat, weights, ball, floor line, text, scenery.
- **Apparel:** Black full-length tights.

## Wellbeing — 2

### WEL001 — Meditating — PILOT

- **Pose:** Calm seated cross-legged pose with upright peach body, eyes gently closed, and gloved hands resting palm-up on the knees.
- **Allowed props:** None.
- **Forbidden props:** Mat, cushion, candles, lotus, aura, text, landscape, scenery.
- **Apparel:** Black full-length tights.

### WEL002 — Yoga Tree Pose

- **Pose:** Balanced front or slight three-quarter tree pose, one simple foot placed against the standing leg below the knee and hands together overhead or at chest height; silhouette must remain stable.
- **Allowed props:** None.
- **Forbidden props:** Mat, blocks, plants, mandala, aura, text, scenery.
- **Apparel:** Black full-length tights.

## Success — 2

### SUC001 — Standing on Winner's Podium — PILOT

- **Pose:** Proud upright victory stance centred on the highest platform, both arms raised or one hand on hip; feet fully supported and visible.
- **Allowed props:** One simple three-level podium with no numbers or words.
- **Forbidden props:** Trophy, medal, flag, confetti, crowd, readable rankings, scenery.
- **Apparel:** Black athletic shorts.

### SUC002 — Holding The Evolved Flag

- **Pose:** Strong three-quarter stance holding one flagpole securely at the side while the flag flows outward without covering the face or body.
- **Allowed props:** One simple flag and pole using the approved Evolved mark only after the exact artwork is supplied as a controlled logo reference.
- **Forbidden props:** Invented or approximate logo, extra writing, second flag, podium, trophy, wind scenery, crowd.
- **Apparel:** Black full-length tights.

## Per-Asset Production Record

When work begins, add this block beneath the relevant asset:

```text
- Status: Prompt prepared | Candidate generated | Awaiting approval | Approved | Promoted
- Prompt file:
- Candidate file:
- Review sheet:
- Human approval date:
- Approved local master:
- Superseded local master:
- Drive file ID/link:
- Sheet link verified:
- Technical QA result:
- Notes:
```

Do not mark `Approved` or `Promoted` without Peter Brown's explicit decision. Do not update the Google Sheet until the corresponding file and link state has been verified.
