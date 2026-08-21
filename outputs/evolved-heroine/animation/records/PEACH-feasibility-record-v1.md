# Peach Animation Feasibility Record v1

**Date:** 2026-08-04  
**Status:** Go for approval-gated layered construction; Motion GUI automation remains permission-gated

## Result

The installed Apple production stack matches the approved phase-one platform:

- Apple Motion 6.3
- Final Cut Pro 11.0.1
- Compressor 5.3
- macOS 26.5.2 on Apple silicon with Metal support

Motion 6.3 successfully rendered an isolated frame from an installed Apple
Motion project to a true 1920 × 1080 RGBA PNG. The decoded alpha plane contained
both fully transparent and fully opaque pixels.

Proof:

`renders/transparent/png-sequences/PEACH-ALPHA-smoke-test-frame0060-v1.png`

The proof establishes that the installed Motion render engine and PNG-alpha
path work. It does not yet prove ProRes 4444 export, a Peach source project,
Final Cut template compatibility, or the Motion-to-Compressor route.

## Automation and control routes

- Motion exposes no AppleScript dictionary.
- macOS Accessibility UI automation is currently disabled for this control
  context.
- Motion's installed internal smoke-test renderer can read a `.motn` file and
  render PNG or OpenEXR frames. This is useful for isolated QA but is not an
  Apple-documented public production API.
- The supported construction route remains Motion's graphical interface.
- Compressor provides an Apple-documented command-line submission route after
  a compatible source and setting exist.

Normal Motion GUI construction and export therefore require Peter to enable
Accessibility control for the Codex host, or to complete the relevant Motion
save/export interactions manually. No permission was bypassed.

## Asset conclusion

No existing PNG is safe as a complete rig base:

- Original calibration authorities contain ambient backdrop, floor/shadow,
  equipment occlusion, large partial-alpha regions, or limited edge clearance.
- Newer approved gesture masters are clean flattened pose descendants, not
  identity or style authorities.
- A visibly rebuilt neutral three-quarter source is unavoidable.

The proposed target is a controlled reconstruction using:

- CHR005 for the primary three-quarter turn and laterality
- CHR002 for neutral facial identity and two-leaf/stem identity
- FND002 for body contour and lower point
- FND004 for hard vintage value separation
- FND001 for supporting palette, texture, apparel, and limb joins
- COA005 and COA007 for pose-only coaching and relaxed-limb references
- FRD001 for the locked anatomical-left shoe implementation

## Go/no-go

**Go**, with these gates:

1. Peter approves the neutral three-quarter reconstruction target.
2. Full layered construction is completed and visually rechecked.
3. Peter approves the layered source before Motion rigging.
4. Motion GUI access is available for the editable rig and documented export
   routes.
5. Final Cut Pro 11.0.1 compatibility is tested empirically because it is older
   than Motion 6.3 and Apple does not publish a compatibility guarantee for this
   exact mixed-version set.

## Official Apple references

- Motion layered PSD import:
  <https://support.apple.com/guide/motion/motn1252ba5a/mac>
- Motion rigs and widgets:
  <https://support.apple.com/guide/motion/motn13f20610/mac>
- Motion Link behavior:
  <https://support.apple.com/guide/motion/link-behavior-motn13745d42/mac>
- Motion transparent backgrounds:
  <https://support.apple.com/guide/motion/motnb8ca82dd/mac>
- Motion movie export:
  <https://support.apple.com/guide/motion/motn189cfcd6/mac>
- Apple ProRes 4444 alpha support:
  <https://support.apple.com/102207>
- Motion template storage and publishing:
  <https://support.apple.com/guide/motion/motn141bd88c/mac>
- Compressor built-in settings:
  <https://support.apple.com/guide/compressor/cpsr4c5ffdc9/mac>
- Compressor command-line submission:
  <https://support.apple.com/guide/compressor/cpsr9be73312/mac>

