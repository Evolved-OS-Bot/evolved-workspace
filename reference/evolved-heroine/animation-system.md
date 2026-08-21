# Evolved Heroine Animation System

**Status:** Approved direction; production system not yet built  
**Owner decision:** 2026-08-04  
**Character:** Peach, the Evolved Heroine  

## Purpose

Create a reusable, controlled 2D animation system that lets Peach appear naturally in video, social, website, email, presentation, and campaign work without redrawing or regenerating her for every project.

The system must preserve the approved vintage athletic-mascot character. Animation is a deployment layer, not permission to redesign Peach or create an alternative master identity.

## What a Proper Animation System Means

A proper system is not an AI-generated video of a PNG and not a collection of one-off motion effects.

It consists of:

1. A layered, approved character rig
2. Defined character pivots and deformation limits
3. A reusable library of approved motions and expressions
4. Channel-ready compositions and export presets
5. Versioned source files and rendered outputs
6. Human approval before a new motion enters the reusable library

This produces repeatable, editable movement while keeping Peach recognisable across every channel.

## Recommended Technical Approach

### Canonical production rig

Build the master rig in Apple Motion 6.3 with a layered PSD/PSB source, using groups, anchor points, rigs, widgets, link behaviours, keyframes, masks, and other native Motion controls.

The canonical phase-one project frame rate is **30 fps**, fixed by Peter Brown
on 4 August 2026. Motion projects, reusable motions, expression tests,
templates, review renders, and phase-one delivery presets must preserve 30 fps
unless a later owner decision explicitly supersedes it.

Why this is the recommended starting point:

- Motion, Final Cut Pro, and Compressor are already installed and owned on Peter Brown's Mac
- Preserves the existing raster ink texture and vintage shading
- Produces transparent video for Canva, Final Cut Pro, CapCut, websites, and social production
- Publishes reusable generators, titles, effects, and parameters directly into Final Cut Pro
- Supports reusable compositions, rig widgets, behaviours, keyframes, motion controls, and Compressor export presets
- Avoids rebuilding the entire character as vector artwork before useful animation can begin
- Avoids adding an Adobe subscription before the Apple-native workflow has been tested

Motion's native rigging is appropriate for the foundation pack's controlled cutout animation. Moho or Adobe After Effects may be reconsidered later if the project requires advanced skeletal deformation, mesh warping, large-scale lip-sync, or an external specialist workflow that materially exceeds Motion's capabilities.

Lottie should not be the canonical master format. The current character is raster artwork with texture and hard shading; a faithful Lottie system would require a separate controlled vector reconstruction. Lottie or Rive may be considered later for lightweight interactive website use.

### Source hierarchy

```text
Approved static master
    ↓
Layered animation construction file
    ↓
Approved animation rig
    ↓
Reusable approved motion
    ↓
Channel-specific rendered derivative
```

No animated output becomes a new identity or style authority.

## Rig Construction

The layered construction file should separate:

- Peach body and approved shading
- Stem
- Each leaf
- Eyes
- Eyelids
- Pupils
- Brows
- Mouth and approved expression shapes
- Rosy cheeks
- Left and right upper arms
- Left and right lower arms
- Left and right gloves
- Left and right upper leg or tube-leg sections where required
- Left and right lower leg or tube-leg sections
- Left and right sneakers
- Athletic shorts or tights
- Reusable props only when needed for a specific rig variant

### Pivot rules

- Arms and legs attach directly to the peach body.
- Limb pivots must preserve simple tube construction.
- Glove and shoe pivots must not create anatomical wrists, ankles, knees, hips, or shoulders.
- The body remains the dominant mass and cannot become a head above a human torso.
- Shoe branding remains on the outward-facing side of the anatomical left shoe.
- Horizontal mirroring is prohibited.

### Deformation rules

Allowed:

- Small whole-body rise and fall
- Restrained vintage-cartoon squash and stretch
- Leaf settling or bounce
- Blinks, pupil movement, brow movement, and approved mouth changes
- Tube-limb bending needed for readable gestures
- Small secondary motion in gloves, shoes, clothing, and props

Not allowed:

- Inflated 3D volume
- Rubber-hose distortion that changes Peach's identity
- Human shoulders, chest, waist, hips, pelvis, buttocks, or anatomical limbs
- Face morphing beyond approved expression language
- Detached, intersecting, or disappearing equipment
- New gradients, lighting, gloss, ambient shadows, or Pixar-like rendering
- Any motion that relocates or reverses left-shoe branding

## Motion Personality

Peach expresses the existing Evolved voice:

- Friendly
- Supportive
- Confident
- Encouraging
- Knowledgeable
- Energetic without being frantic
- Warm without becoming childish

Motion should feel purposeful and controlled. Strength movements feel stable and mechanically credible. Coaching movements feel clear and welcoming. Celebrations feel joyful without becoming chaotic.

## Recommended First Motion Library

### Foundation pack

Build these first because they cover the largest number of marketing uses:

1. **Idle loop** — gentle whole-body settle, leaf secondary motion, occasional blink
2. **Friendly wave** — greeting, welcome, community, onboarding
3. **Point left** — headline, product, CTA, or on-screen information
4. **Point right** — alternate layout direction without flipping the character
5. **Thumbs up** — encouragement, confirmation, next step
6. **Double-arm victory** — celebration, milestone, success
7. **Explaining gesture** — education, carousel, course, FAQ, science
8. **Listening reaction** — member support, question, objection, consultation
9. **Walking entrance and exit** — scene transitions and video overlays
10. **CTA attention loop** — restrained gesture toward a button or offer area

Each directional action must be built separately. Never create the opposite direction by flipping a rendered asset.

### Expression pack

- Neutral friendly
- Warm smile
- Confident smile
- Curious/thinking
- Encouraging
- Celebratory
- Calm/wellbeing
- Focused/coaching

Expressions should be built from approved existing poses and never expand the character's facial language without review.

### Later specialist packs

- Strength and exercise demonstrations
- Healthy habits
- Seasonal and event animations
- Achievement and celebration
- Coaching and onboarding
- Website interface states
- Science and educational explainers

## Composition Templates

Create reusable templates for:

| Format | Canvas | Typical use |
| --- | --- | --- |
| Vertical social | 1080 × 1920 | Reels, Stories, short-form video |
| Portrait feed | 1080 × 1350 | Instagram and Facebook feed |
| Square | 1080 × 1080 | Social, Canva, campaign tiles |
| Landscape video | 1920 × 1080 | YouTube, presentations, website video |
| Transparent master | 3840 × 2160 working area | High-quality reusable overlay rendering |

Templates should include safe zones for:

- Headline
- Supporting copy
- CTA
- Captions
- Platform interface overlays
- Member photography

## Export Standards

### Archival and editable

- Apple Motion project, published Final Cut template where applicable, and linked layered source
- Versioned source package with no missing dependencies
- PNG sequence with transparency for durable archival interchange

### Video production

- Apple ProRes 4444 with alpha as the high-quality transparent master
- WebM with alpha for compatible website or lightweight digital use
- H.264 MP4 with an intentional background for direct social publishing

### Static fallback

- PNG for transparent still frames
- WebP or AVIF for optimised website stills
- GIF only when required by a platform; never treat GIF as the quality master

Every export should use sRGB colour handling and preserve the approved colours as closely as the destination permits.

## File Structure

```text
outputs/evolved-heroine/animation/
├── rigs/
│   ├── source/
│   └── approved/
├── motions/
│   ├── candidates/
│   └── approved/
├── renders/
│   ├── transparent/
│   ├── social/
│   ├── website/
│   └── video/
├── templates/
└── review/
```

Recommended naming:

```text
PEACH-RIG-three-quarter-v1.motn
PEACH-MOTION-friendly-wave-candidate-v1.mov
PEACH-MOTION-friendly-wave-approved-v1.mov
PEACH-MOTION-point-left-instagram-story-v1.webm
```

## Approval and Versioning

1. Select the approved static references for the rig or motion.
2. Build the layered source without altering identity or rendering style.
3. Create the candidate rig or motion.
4. Render a review sheet or review video on neutral, light, and dark backgrounds.
5. Check construction, motion mechanics, loop quality, transparency, colour, edges, props, and shoe branding.
6. Obtain Peter Brown's explicit approval.
7. Promote the source and rendered motion to the approved animation library.
8. Preserve prior versions rather than overwriting silently.
9. Record the approved motion, source version, exports, and intended uses.

Approval of one motion does not approve every motion produced from the rig.

## Website Performance Rules

- Do not autoplay large transparent video assets above the fold without a measured performance reason.
- Respect reduced-motion browser preferences.
- Provide a static approved fallback.
- Lazy-load non-critical animation.
- Use animation to guide attention, not compete with the CTA or member evidence.
- Measure page speed, layout stability, and conversion impact.

## Recommended First Build

Start with one three-quarter Peach rig based on the approved neutral, friendly, and coaching references.

Deliver:

- One approved layered master rig
- The ten-motion foundation pack
- The eight-expression pack
- Five composition templates
- ProRes 4444, WebM-alpha, MP4, and static PNG export presets
- One review reel showing every motion on light, dark, and transparent-checker backgrounds
- One usage index recording motion names, intended messages, source files, and approved exports

This first build would cover the majority of practical marketing needs without attempting a full animated series.

## Decisions Required Before Production

Before rigging begins, confirm:

1. Whether the first rig is front-facing, three-quarter, or both
2. Whether an external animator will receive the layered build package
3. Whether spoken dialogue or lip-sync is in scope
4. Whether website-interactive animation is needed in phase one
5. The first real campaign or video that will serve as the acceptance test
