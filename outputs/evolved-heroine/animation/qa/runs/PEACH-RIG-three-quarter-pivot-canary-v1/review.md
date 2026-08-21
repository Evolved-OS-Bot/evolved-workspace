# Peach Right-Leg Pivot Canary v1

**Status:** Pivot placement and neutral compensation pass; root-cover and
rotation stress tests pending

The reversible Apple Motion 6.3 canary moves the anatomical-right upper-leg
anchor to the provisional source-canvas coordinate `(582, 680)`. Motion stores
that point as anchor `(-45, -53)`. Matching position compensation
`(-45, -53)` preserves the zero state exactly.

The supported 1254 × 1254, 16-bit/color RGBA sRGB export is byte-identical to
the proven neutral stack export. Both have SHA-256
`17dd880b122313934b403d116756643219c89e3c209d75c848861a52e054b2b2`.

Motion exposes and selects its native Bezier and Rectangle Mask tools, and the
source-derived duplicate was correctly selected. Synthetic canvas drawing
gestures did not create a native mask object. The failed duplicate was removed,
so the saved canary is pivot-only and remains neutral-exact.

## Next safe action

Create the fixed body-space root-cover mask through a native Motion canvas
interaction. Only then test neutral, ±6°, ±12°, and modest overtravel on
transparent, light, and dark backgrounds.

This is technical evidence only. It does not approve the pivot, root-cover
mask, rig, motions, expressions, templates, further exports, or deployment.
