# Cancellation contact-evidence and owner-escalation acceptance

**Date:** 2026-08-04  
**Scope:** Eight Piper-led membership-cancellation reason workflows.  
**Excluded:** `MC: Other (Booked Call)` because the member explicitly requests manager contact.

## Approved control

- A member reply during an active cancellation notice is sufficient contact evidence.
- The automation writes the existing compatibility tag `cs: contact made`; Piper is not the sole writer.
- Call attempts, voicemail, ringing and generic `Completed` status do not count.
- A call may write evidence only if HighLevel can natively require an outbound connected call lasting at least 60 seconds.
- The Day-14 path checks evidence again immediately before escalation.
- Megan receives a same-day review task only when no evidence exists.
- No automatic client SMS is sent in Megan's name.

## Baseline

- All eight Piper-led workflows were published and used the manual `cs: contact made` tag at their early checks.
- Their Day-14 no-contact branch contained an owner notification followed by an automatic client SMS in Megan's name.
- The booked-call exception remained a separate published workflow.
- One investigated active notice showed meaningful staff contact but no compatibility tag, allowing the automatic owner path to run.

## Build verification

### Live controls

- Created and API read-back verified:
  - `CS: Contact Evidence Source` (`wIhH5FlD4tZlw4vrzuck`)
  - `CS: Contact Evidence At` (`dMZBb1wwQW9OqZ42df5d`)
- Published and reload-verified `CS: Contact Evidence - Member Reply`
  (`06363191-7fbc-4b60-b6d9-000d521cef87`).
- Trigger: `Customer Replied`.
- Trigger filter: `CS: Cancellation Status = Notice Active`.
- Actions:
  - `CS: Contact Evidence Source = Member Reply`
  - add compatibility tag `cs: contact made`
- HighLevel does not expose a reliable native current-time value in this
  action, so the helper does not write `CS: Contact Evidence At`. Historical
  reconciliation writes the actual event timestamp through the governed
  backfill tool.

### Native call boundary

The live `Call details` trigger exposes `Call direction`, `Call status`,
`Custom disposition`, `In workflow` and contact-field filters. It does not
expose call duration. No call-evidence helper was published. Generic
`Completed`, voicemail, ringing and short calls therefore cannot suppress
escalation automatically.

### Eight reason workflows

The following workflows were saved, reloaded and verified as Published:

| Workflow | ID | Verified result |
|---|---|---|
| MC: Financial | `cf2d159c-2704-4865-8611-d36fbddd01a7` | Automatic owner SMS absent; Megan review task present |
| MC: Health/Injury | `df73b324-e02b-4961-b017-4c2a9f235dbb` | Automatic owner SMS absent; Megan review task present |
| MC: Moving/Travel | `93997227-0272-4aa0-a0ec-da56938f3901` | Automatic owner SMS absent; Megan review task present |
| MC: New Gym | `4300ef4f-7ba6-4ac2-b603-5cc45e2df495` | Automatic owner SMS absent; Megan review task present |
| MC: New Style | `49275845-d251-4847-9254-b08a976963b4` | Automatic owner SMS absent; Megan review task present |
| MC: Other | `4f9ec2c2-4d59-4c69-8a51-2ec3b9eccc9b` | Automatic owner SMS absent; Megan review task present |
| MC: Results/Value | `bc2fc64e-f02c-49f9-bc60-7434fbea1588` | Automatic owner SMS absent; Megan review task present |
| MC: Schedule/Time | `0a999c4e-2951-4670-974f-632969c37b56` | Automatic owner SMS absent; Megan review task present |

The replacement action is `14. Megan review - no contact evidence`. It is
assigned to Megan Brown, due the same day, prohibits an automatic message and
instructs Megan to review the full conversation and call history before
choosing any personal outreach.

The existing tag gates remain the final evidence control on the no-contact
path. The separate `MC: Other (Booked Call)`
(`62c34799-0de4-4281-b5e3-bab95ae70eb9`) was not changed.

## In-flight reconciliation

The complete live Notice Period audit found four open opportunities:

- Lucinda Gibson — 10 inbound SMS replies during the notice; backfilled
  `Member Reply`, `cs: contact made`, and the first qualifying timestamp
  `2026-07-16T00:57:23.437Z`.
- Sarah Loga — 25 inbound SMS replies during the notice; backfilled
  `Member Reply`, `cs: contact made`, and the first qualifying timestamp
  `2026-07-13T02:59:28.148Z`.
- Elizabeth Winter — no qualifying member reply; left untagged.
- Rachael Kolmajer — no qualifying member reply; left untagged.

Both backfills passed immediate API read-back. No member message was sent,
and no billing, access, appointment, opportunity, notice-date or cancellation
state was changed.

## Acceptance result

- PASS — member replies during an active notice automatically write evidence.
- PASS — `Completed` alone cannot write evidence; call automation failed closed.
- PASS — all eight in-scope workflows contain a same-day Megan review task and
  no automatic Day-14 client SMS in Megan's name.
- PASS — all four active notices were reconciled from complete conversation
  evidence.
- PASS — no client-facing test message was delivered.
