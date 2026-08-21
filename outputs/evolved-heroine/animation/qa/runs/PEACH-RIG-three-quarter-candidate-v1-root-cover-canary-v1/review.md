# Peach Anatomical-Right Root-Cover Canary v1

**Status:** Technical failure; neutral restoration passes, but the root cover
and incomplete leg chain fail the rotation stress gate.

## Result

The native Apple Motion 6.3 canary retains the provisional anatomical-right
upper-leg pivot at source coordinate `(582, 680)`, stored as Motion anchor and
matching position compensation `(-45, -53)`.

The supported neutral v4 export has zero changed decoded RGBA pixels against
the approved v11 Motion reference under the recorded Pillow RGBA comparison:

- Reference SHA-256:
  `6b1d7fed335a6c841866a77f6cb15976b91b4015347b6f5c4b25fe40a1e528ca`
- Neutral v4 SHA-256:
  `bf8724ffd447e9803d444e21937a6bbfefea4543c315f946cd49c653ec41eafa`
- Decoded changed pixels: `0`

This neutral result does not extend to rotation.

## Corrected stress sweep

The first labelled sweep was invalid because Motion's numeric angle field had
not been committed before Share. Every first-pass file was neutral. Those
files are excluded from the review sheets and cannot support an angle claim.

The corrected v2 captures commit and independently render:

| Angle | SHA-256 | Result |
| --- | --- | --- |
| `-12°` | `d749bb032a4989eccc01bb68091c330e65c407eae97b66cfa7073886e509e039` | Fail |
| `-6°` | `6242af1d07af59797245a8d836cba80871188a5e83636931365c67ffdbdf5ec9` | Fail |
| `0°` | `bf8724ffd447e9803d444e21937a6bbfefea4543c315f946cd49c653ec41eafa` | Neutral-only pass |
| `+6°` | `1c58b9695cdbee700287693688151bc20103db87f8d1b799fa627329cca1d7ac` | Fail |
| `+12°` | `a20dd2aadd183b7219b374526925f72b8b3783168e4b19473bb447afc7d018f3` | Fail |
| `+15°` overtravel | `0ae9e9521392833305acd885681b2b5a60e22f4a7e69f160567be2a1f68dd8c2` | Fail, diagnostic only |

The fixed body-space duplicate is sourced from the approved anatomical-right
upper-leg pixels and carries a direct native Bezier mask. Its rendered result
fails:

- the cover appears as a rounded opaque peach-colour lobe around the lower
  upper-leg or knee seam instead of remaining hidden at the root;
- positive rotation opens a sharp triangular dark or transparent wedge below
  the shorts;
- every nonzero v2 angle exposes a hard upper-leg to lower-leg discontinuity;
- the same defects remain visible on checkerboard, light neutral, and dark
  plum backgrounds;
- `+15°` overtravel makes the wedge and displaced lobe more pronounced.

The full-body sweep also confirms that Peach was not mirrored and the
`Evolved` mark remains only on the anatomical-left shoe. Those preserved
identity controls do not offset the failed leg construction.

## Later diagnostics

A later linked-chain `-12°` test moved the lower leg and shoe with the upper
leg, but its covered and no-cover files are byte-identical at SHA-256
`55cc373d644528ab2e633c9daabfb40294406a974c7d6ab1709ec8f7a598ab17`.
The tested cover state therefore contributed no pixels to the exposed root
gap.

A later moving-root-mask neutral v3 export restored strict byte parity with
the approved reference at SHA-256 `6b1d7fed...`, but no complete accepted
rotated sweep was produced from it.

The exact-path inverted-complement neutral diagnostic preserved alpha support
topology but still changed 229 visible pixels in bounding box
`(552, 748)–(602, 835)`. Its SHA-256 is
`3883e37bc984fa01339c3d7ea6dd96a1667a9710d03776678f11850f064cc54d`.

These diagnostics narrow the next construction step, but none is a passed
root-cover implementation.

## Evidence

- Root close-up on checker, light, and dark backgrounds:
  `PEACH-RIG-three-quarter-candidate-v1-ANAT-R-root-cover-stress-grid-v1.png`
- Full-body corrected v2 sweep on checker:
  `PEACH-RIG-three-quarter-candidate-v1-ANAT-R-full-body-sweep-v1.png`
- Machine-readable result:
  `qa-report.json`

## Next safe action

Keep this run as failed evidence. Complete the anatomical-right upper-leg,
lower-leg, and shoe chain, then build a source-derived root socket that:

1. remains fully hidden and exact at neutral;
2. produces a real covered-versus-uncovered pixel delta only inside the
   exposed root gap;
3. introduces no wedge, floating patch, double outline, or texture break; and
4. passes a fresh `-12°, -6°, 0°, +6°, +12°` sweep on checker, light, and dark
   backgrounds.

This record does not approve the pivot, root cover, leg chain, rig, motion,
expression, template, reusable export, deployment, or external handoff. No
human approval is claimed.
