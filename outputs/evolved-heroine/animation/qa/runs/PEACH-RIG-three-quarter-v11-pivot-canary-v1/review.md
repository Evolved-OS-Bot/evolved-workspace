# Peach v11 Motion Neutral and Pivot Canary

**Status:** Approved-v11 relink and strict transparent neutral parity pass;
root-cover and rotation stress tests pending

Apple Motion 6.3 opened the corrected approved v11 identity base at 1254 ×
1254, 30 fps, with all 29 PNG layers online and no v10 media references.
Motion's supported **Save Current Frame** route used PNG, canvas color space,
and **Color + Alpha**.

The 29-layer stack export and a separately opened single-image v11 reference
export are byte-for-byte identical. Both are 16-bit/color RGBA PNG files with
SHA-256:

`6b1d7fed335a6c841866a77f6cb15976b91b4015347b6f5c4b25fe40a1e528ca`

This strict parity proves the approved 4,755-pixel shoe opacity correction is
preserved through Motion: 3,822 pixels in the anatomical-right blank shoe and
933 pixels in the anatomical-left shoe art. The locked `Evolved` brand remains
on the anatomical-left shoe only, and no horizontal flip is present.

The reversible anatomical-right upper-leg pivot remains at source-canvas
coordinate `(582, 680)`, stored as Motion anchor `(-45, -53)` with matching
position compensation. Its zero state is exact under the supported Motion
comparison.

## Next safe action

Create a native candidate copy, build the complete rig topology, and add the
fixed body-space source-derived right-leg root cover. Only then test the
prescribed `-12, -6, 0, +6, +12` degree sweep on checker, light, and dark
backgrounds.

This is technical evidence only. It does not approve the pivot, root-cover
mask, rig, motions, expressions, templates, further exports, or deployment.
