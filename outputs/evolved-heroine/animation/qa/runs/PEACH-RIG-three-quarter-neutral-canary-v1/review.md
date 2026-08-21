# Peach Motion Neutral Canary v1

**Status:** Technical pass; supported Motion export has exact neutral parity

## Result

The native Motion project is structurally correct:

- 1254 × 1254, transparent, Standard Gamut SDR, progressive, 30 fps
- 29 separate approved PNG stills
- Image Sequence disabled
- exact approved manifest order
- native locks on body/shading, face-field texture and left-shoe brand
- valid 1254 × 1254, 16-bit/color transparent RGBA sRGB export through Motion's
  supported Save Current Frame path
- byte-identical supported exports from the ordered 29-layer stack and the
  separate single-neutral Motion reference
- zero differing RGB or alpha pixels

Both supported exports have SHA-256
`17dd880b122313934b403d116756643219c89e3c209d75c848861a52e054b2b2`.
Byte comparison and normalized pixel comparison are both exact.

An isolated 8-bit linear-renderer diagnostic previously showed 35,292 RGB
differences, zero alpha differences and a maximum channel delta of 5/255. The
supported 16-bit Motion exports resolve that discrepancy exactly, so the
8-bit result remains diagnostic evidence only and is not an acceptance failure.

## Evidence

- 29-layer native project:
  `../../../rigs/working/PEACH-RIG-three-quarter-candidate-v1/PEACH-RIG-three-quarter-neutral-canary-v1.motn`
- Single-neutral native comparison project:
  `../../../rigs/working/PEACH-RIG-three-quarter-candidate-v1/PEACH-RIG-three-quarter-neutral-reference-canary-v1.motn`
- Supported 29-layer export:
  `../../../renders/transparent/png-sequences/PEACH-RIG-three-quarter-candidate-v1-neutral-share-v1.png`
- Supported single-neutral export:
  `../../../renders/transparent/png-sequences/PEACH-RIG-three-quarter-neutral-reference-share-v1.png`
- Isolated-renderer 29-layer diagnostic:
  `../../../renders/transparent/png-sequences/PEACH-RIG-three-quarter-candidate-v1-neutral-canary.png`
- Isolated-renderer single-neutral diagnostic:
  `../../../renders/transparent/png-sequences/PEACH-RIG-three-quarter-neutral-reference-canary-v1.png`
- Difference mask:
  `motion-to-motion-difference-mask.png`
- Amplified difference:
  `motion-to-motion-difference-amplified-64x.png`
- Machine-readable report:
  `qa-report.json`

## Next safe action

Build one reversible upper-leg pivot plus its fixed source-derived body-space
root cover, then test neutral, ±6°, ±12° and modest overtravel on transparent,
light, and dark backgrounds.

This technical pass does not approve the rig, provisional pivots, root-cover
masks, motions, expressions, templates, further exports, or deployment.
