# Active Client Cohort Reconciliation

**As of:** 27 July 2026  
**Rule:** `active-client-cohort-v1`  
**Mode:** Read-only, shadow only  
**Production cutover:** Not authorised

## Confirmed result

| Measure | Count |
|---|---:|
| Legacy hub lifecycle count previously labelled active signal | 191 |
| Current active-source signals among the compared identities | 151 |
| Governed confirmed active clients | 127 |
| Identities present in both compared cohorts | 127 |
| Legacy-only identities | 64 |
| Governed-only identities | 0 |
| Symmetric identity difference | 64 |
| Net count overstatement | 64 |

The former 191 label was incorrect. It combined 152 real source-signal
identities with 39 identities that had only a non-empty cancellation field.
Current source state is overlaid on that frozen audit baseline. One historical
source-signal identity is now correctly retired following an owner-approved
cancellation correction, so the current signal count is 151.

## Identity-difference buckets

| Exclusive primary reason | Count |
|---|---:|
| Cancellation metadata without an active source signal | 39 |
| Staff, owner or approved internal access | 10 |
| Approved complimentary membership outside the KPI | 1 |
| Online service outside the SGPT/PT KPI | 3 |
| Arrears evidence retained for revenue review only | 5 |
| Active roster row added after the governed snapshot | 5 |
| Historical active signal now retired | 1 |
| Governed approved hold without an active source signal | 0 |
| Peter decision required | 0 |
| **Total identity difference** | **64** |

## Owner review

No identities require Peter's decision. Every identity in the 64-person difference now has a governed disposition.

## Paid and entitled status

This run does not publish a paid-or-entitled total. The accepted membership
snapshot contains Stripe contract status, not complete payment evidence, and
Trainerize proves access only.

Paid or entitled must be projected separately from Stripe payment events,
specific PT Minder debit events, PIA or pack evidence, approved holds, pending
debits, future starts and final-access dates. Until that evidence is accepted,
the dashboard must display this measure as unavailable.

## Safety gates

- The reconciliation command is read-only. Eliza Lebsanft's separate,
  owner-authorised cancellation correction was completed across GHL,
  Trainerize and the governed workbook before this shadow report was refreshed.
  Emma Johnson's owner-authorised Active SGPT restoration is recorded as a
  timing difference until the next governed roster snapshot is accepted.
  Erica Asler, Madison McKiernan and Reemi Shah are also recorded as
  owner-approved timing corrections. Sue Goodwin is classified as a current
  Evolved Anywhere online client outside the SGPT/PT KPI, and Tsana Leatham is classified
  as an approved complimentary member outside the KPI.
- Existing production consumers remain on their protected inputs.
- No cutover is allowed until the next governed snapshot includes all five
  owner-approved timing additions with exact identity parity, the
  paid-or-entitled projection is complete and two shadow parity cycles pass.

## Validation

The reporting-control, operating-hub, revenue-control, PT-continuity,
retention-intelligence, Trainerize-performance and membership-reconciliation
suites pass: 184 tests.
