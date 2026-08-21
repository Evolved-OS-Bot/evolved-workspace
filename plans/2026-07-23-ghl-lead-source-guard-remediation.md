# GHL Lead Source Guard Remediation

**Status:** Completed  
**Date:** 23 July 2026

## Objective

Preserve `Lead Source` as the original first-touch source while retaining every existing 30DNNC form, tag, spreadsheet and nurture action.

## Live finding

Eleven published 30DNNC form-submission workflows directly update `Lead Source` without checking whether the field is blank. Five paid routes assign `Paid Social - Meta`; five organic routes and the generic route assign legacy `Organic`.

## Implementation

1. Build a published guarded workflow for the generic and five organic 30DNNC forms. Assign `Website Organic` only when `Lead Source` is blank.
2. Build a published guarded workflow for the five paid 30DNNC forms. Assign `Paid Social - Meta` only when `Lead Source` is blank.
3. Test both workflows using a blank-source contact and an already-populated contact.
4. Remove only the direct `Update 'Lead Source' field` action from the eleven existing workflows.
5. Verify all existing non-source actions remain intact and all workflows remain published.
6. Update the roadmap and governance register with the final live state.

## Safety controls

- Do not block existing 30DNNC workflows from running for known contacts.
- Do not remove any tag, spreadsheet, notification or nurture action.
- Do not repurpose legacy `Organic`; retain it for historical contacts.
- Do not publish the guarded workflows until their form coverage and blank-field condition are confirmed.
- Do not remove existing source actions until both new guarded workflows are live and tested.

## Completion record

Completed 23 July 2026.

- Published `LS: Guarded 30DNNC Website Organic` (`22ee9373-c366-4021-bdb4-fa205c34cd4a`) for the generic form and five organic forms. It assigns `Website Organic` only when `Lead Source` is empty.
- Published `LS: Guarded 30DNNC Paid Social - Meta` (`dc574784-bc9e-47e3-b1d5-6c982f3deadd`) for the five paid forms. It assigns `Paid Social - Meta` only when `Lead Source` is empty.
- Used the existing Peter Brown dummy record to verify both paths. The paid guard populated a blank source with `Paid Social - Meta`; the organic guard then preserved that populated value.
- Removed only the direct `Update 'Lead Source' field` action from all eleven original 30DNNC form-submission workflows.
- Verified each original workflow remained published after saving. Existing tags, notifications, waits, spreadsheets and nurture actions were retained.
