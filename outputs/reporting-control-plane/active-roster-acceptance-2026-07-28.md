# Active Roster Acceptance

> Historical checkpoint. The later prepaid-pack promotion is recorded in `prepaid-pack-entitlement-promotion-2026-07-28.md`.

**As of:** 28 July 2026  
**Rule:** `active-client-cohort-v2`  
**Mode:** Railway shadow control  
**Member-system writes:** None

## Accepted result

| Measure | Count |
|---|---:|
| Live Google roster candidate | 132 |
| Candidate service relationships | 143 |
| Previously accepted governed clients | 127 |
| Candidate additions since the original acceptance | 5 |
| Candidate removals | 0 |
| Additions promoted through the evidence gate | 4 |
| Governed active clients after promotion | 131 |
| Governed service relationships after promotion | 142 |
| Current roster candidates still requiring review | 1 |

The promotion required an exact current roster identity, active GHL lifecycle
and a confirmed commercial entitlement matching every candidate service.
Four additions met that full gate.

One PT candidate remains outside the accepted cohort because the current hub
snapshot does not yet represent her approved paid-in-full pack as a commercial
entitlement. The operational correction is not reversed; the identity remains
quarantined until that evidence type is accepted by the shared contract.

## Safety behaviour

- Any removal from the accepted cohort blocks promotion.
- A changed candidate snapshot blocks promotion and must be reviewed again.
- Missing identities and duplicate same-service rows block publication.
- Trainerize access is supporting evidence, not payment or lifecycle proof.
- Candidate collection runs at the start of the existing Railway revenue
  audit; it creates no additional schedule.
- No Google Sheet, GHL, Stripe, Trainerize or PT Minder record was changed.
