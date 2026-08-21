# Prepaid Pack Entitlement Promotion

Date: 28 July 2026  
Runtime: Railway only  
Mode: Shadow and read-only against member systems

## Outcome

Historical note: the 76 verified and 56 pending figures below used the original
person-level coverage rule. The service-level queue deployed later on 28 July
supersedes them with 68 fully covered clients and 64 clients carrying 68
service-level gaps. The roster counts and prepaid-pack conclusion remain valid.

The governed active roster now exactly matches the current Google SGPT/PT roster:

- 132 governed active clients;
- 143 governed service relationships;
- 132 live roster candidates;
- zero candidate additions;
- zero candidate removals;
- 76 governed clients with confirmed commercial entitlement;
- 56 governed clients awaiting complete entitlement evidence;
- two historical decision cases outside the current roster gap.

Accepted governed snapshot: `20260727T221407Z-a0748077`  
Accepted candidate snapshot: `20260727T220111Z-695790c4`  
Verified pack snapshot: `20260727T221317Z-274e16a7`

## Vavaa Mawuli

Vavaa's current PT status now reconciles across the governed sources:

- GHL lifecycle: active `PT Only`;
- Trainerize access: active;
- recurring Stripe entitlement: absent, as expected for a prepaid pack;
- prepaid Stripe pack: confirmed A$1,200 successful one-off payment with an explicit approved beneficiary mapping;
- Google Sheet: current Active PT endpoint;
- governed disposition: confirmed active.

The payment confirms commercial entitlement. It does not assert an exact remaining-session balance. Appointment sequence conflicts remain fail-closed in the separate pack-delivery review.

## Safety Controls

- Only successful, non-invoice Stripe PaymentIntents can enter the pack source.
- A PaymentIntent must be explicitly mapped to its GHL beneficiary.
- Same-email matching, amount matching and appointment text cannot create entitlement.
- GHL remains lifecycle authority.
- The exact `pt only` tag is current only when no cancellation, termination or `old pt client` control overrides it.
- The generic `personal training` tag alone remains insufficient.
- The pack publisher supersedes removed mappings through complete snapshots.
- No client, payment, membership, booking or Google Sheet record was changed by this architecture build.
- No Codex or harness schedule was created.

## Verification

- 206 connected tests passed.
- Hub deployment: `6ac8d6af-fffa-423a-807d-133a069c74c9`.
- Retention deployment: `7f1fabe2-a6ab-4168-8121-edc94eb7e010`.
- PT publisher deployments: `39152bef-0255-4373-bff0-a369a1e9fe74` and `f81541f0-7a20-439c-8515-f9910dda04c8`.
- Railway PT verification run: `67e8af2d-71b8-4508-9e03-666c41456725`.
- CEO dashboard visually verified at 132 governed clients, 143 relationships and exact roster identity match.
