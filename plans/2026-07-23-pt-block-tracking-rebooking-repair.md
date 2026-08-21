# PT Block Tracking and Rebooking Repair

**Status:** Completed  
**Date:** 23 July 2026

## Objective

Repair the published GHL workflow `Internal Notification (Rebook Client)` (`280a2ca3-0f51-4f03-b5dc-c271c2ef8075`) so it records the current 13-week PT block once, covers every current PT delivery calendar and creates an accountable rebooking handoff without premature field overwrites.

## Governing decisions

- `PT Block Start`, `PT Block Trainer` and `PT Block Service` describe the current 13-week PT block.
- The first qualifying PT booking while the tracking tag is absent starts the block and writes the fields.
- Admin Eve owns the rebooking task. The contact owner remains informed as the member-facing or delivery owner.
- The rebooking prompt starts at Week 10, but the tracking tag remains in place until the complete 13-week block has elapsed.
- Every current trainer's 30-, 45- and 60-minute PT calendar is in scope: Megan, Piper, Nora, Katrina and Leisa.

## Implementation

1. Rename the workflow to `PT: Block Tracking & 13-Week Rebooking`.
2. Remove the six invalid Marnie and Wileen calendar triggers.
3. Retain the six valid Megan and Leisa triggers.
4. Add the nine missing Piper, Nora and Katrina calendar triggers.
5. Correct both `24 weeks` notifications to `13 weeks`.
6. Assign the rebooking task and the Admin notification to Admin Eve; retain the contact-owner notification and final email.
7. Keep the Week 10 initial handoff, replace the former five-day wait with a 21-day wait, send the final internal email at Week 13 and then remove the tracking tag. This makes the lock span 91 days.
8. Disable general re-entry and multiple-opportunity execution. Appointment-trigger re-entry remains available after the prior execution has ended, as required for a later block.
9. Save, verify the workflow remains published and update the audit records.

## Safety controls

- Do not change PT pricing, agreement, cancellation or onboarding workflows.
- Do not change the three PT Block custom fields or their merge keys.
- Do not remove the existing tag guard.
- Do not remove any valid Megan or Leisa calendar trigger.
- Do not publish a partial trigger state if the existing workflow becomes unpublished during editing.

## Completion record

Completed and live-verified 23 July 2026.

- Renamed the workflow to `PT: Block Tracking & 13-Week Rebooking`.
- Retained the six valid Megan and Leisa triggers.
- Added Nora and Piper at 30, 45 and 60 minutes.
- Converted the three obsolete Marnie triggers to Katrina's 30-, 45- and 60-minute calendars.
- Deleted the three obsolete Wileen triggers. The final workflow has 15 current PT calendar triggers and no Marnie or Wileen dependency.
- Corrected both `24 weeks` notifications to `13 weeks`.
- Assigned the rebooking task and specific Admin notification to Admin Eve. The contact-owner notification and final internal email remain.
- Replaced the five-day wait with `Wait until Week 13`, configured as 21 days after the Week 10 handoff. The tracking tag is now removed after 91 days rather than after 75 days.
- Disabled general re-entry and multiple-opportunity execution. Appointment-trigger re-entry remains available after the previous execution ends.
- Saved and confirmed the workflow remained published.
