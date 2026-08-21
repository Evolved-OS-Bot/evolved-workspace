# Service-Level Entitlement Exception Queue

Date: 28 July 2026  
Runtime: Railway only  
Mode: Shadow and read-only against member systems

## Outcome

Historical note: the 68 verified, 64 pending and 68 service-gap figures below
were the first service-level baseline. Revenue Control evidence promotion later
on 28 July superseded them with 93 verified clients, 39 pending clients and 41
service gaps. The service-level definition and queue architecture remain valid.

The operating-data hub now tests commercial coverage at the governed service
relationship level:

- 132 governed active clients;
- 143 governed SGPT/PT relationships;
- 68 clients fully covered across every governed service;
- 64 clients with incomplete commercial coverage;
- 68 uncovered service relationships;
- eight deterministic exception buckets;
- 22 high-priority service gaps.

This is a correction in definition, not a deterioration in the client base. The
earlier person-level rule counted a cross-service client as verified when either
SGPT or PT had evidence. The corrected rule requires compatible confirmed
evidence for every governed service.

## Live Queue

| Bucket | Priority | Clients | Service gaps | Owner |
| --- | --- | ---: | ---: | --- |
| Lifecycle correction required | High | 4 | 4 | Admin Eve |
| Payment retry in progress | High | 6 | 6 | Admin Eve |
| Payment and booking unresolved | High | 12 | 12 | Admin Eve |
| PIA or prepaid pack evidence | Medium | 6 | 6 | Admin Eve |
| Collecting evidence not yet shared | Medium | 27 | 30 | Admin Eve |
| Payment current, booking gap | Medium | 3 | 3 | Admin Eve |
| Approved hold evidence | Low | 6 | 6 | Admin Eve |
| Approved future start | Low | 1 | 1 | Admin Eve |

The bucket totals overlap at client level where one person has more than one
service gap. Service-gap totals are exact. Queue records are evidence states and
must not be interpreted as automatic debts.

## Architecture

- SGPT is covered by confirmed SGPT or Fast Track evidence.
- PT is covered only by confirmed personal-training evidence.
- Every uncovered service receives one deterministic bucket, priority, owner
  and next action.
- The CEO dashboard and CEO report expose aggregate queue counts only.
- `GET /api/v1/entitlement-exceptions` exposes identified cases only when the
  caller supplies the hub secret.
- GHL remains lifecycle authority; payment evidence cannot promote lifecycle.
- PT Minder displayed balances and its Charge function remain excluded from
  debt logic.

## Verification

- 210 connected hub and controller tests passed.
- Hub deployment: `48186493-4a4e-450e-8c47-15e1d03f1248`.
- Production dashboard verified at 132 governed clients, 143 relationships,
  68 fully covered clients, 64 pending clients and 68 service gaps.
- Current roster parity remains exact.
- No client, payment, membership, booking or Google Sheet record was changed.
- No Codex or harness schedule was created.

## Next Build

This migration was completed later on 28 July. The original next action was to
publish the 30 existing
`CLEAN_COLLECTING` service gaps across 27 clients from the revenue/controller
evidence into the shared commercial contract. Promotion must remain fail-closed
on exact identity, service type and current payment evidence.
