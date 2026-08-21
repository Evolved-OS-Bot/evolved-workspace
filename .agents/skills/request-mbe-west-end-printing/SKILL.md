---
name: request-mbe-west-end-printing
description: Prepare, validate, upload, and submit print, lamination, binding, or finishing requests to MBE West End for The Evolved All Female Gym. Use when the user asks to print or laminate a supplied image, PDF, document, poster, sign, or similar file through MBE West End, including checking print readiness, preparing a print-ready file, completing the upload form, or following up on a print request.
---

# Request MBE West End Printing

## Overview

Prepare the file and submit a friendly, accurate request through MBE West End's upload form. Do not submit until the user confirms the completed request at action time.

## Customer details

Use these details unless the user supplies different information:

- Company: The Evolved All Female Gym
- First name: Peter
- Surname: Brown
- Phone: 0420 863 721
- Email: info@theevolvedgym.com.au
- State: QLD
- Centre: MBE West End
- Upload form: https://www.mbe.com.au/file-upload/?area=QLD&store=westend

Do not substitute peter@theevolvedgym.com.au for the preferred email.

## Workflow

### 1. Establish the job specifications

There are no default production specifications. Confirm the details needed for the current job:

- Quantity
- Finished size and orientation
- Colour or black and white
- Single-sided or double-sided
- Paper stock, or permission for MBE to recommend it
- Finishing, including lamination type and finish
- Bleed and trimming
- Collection or delivery
- Required date

Ask only for details that cannot be inferred safely from the supplied file or the user's request.

### 2. Inspect and prepare the file

Inspect the source before uploading:

- Confirm page count, dimensions, aspect ratio, resolution, and orientation.
- Render PDFs for visual review and verify trim and bleed boxes when relevant.
- Prefer PDF Print for finished artwork.
- Use a standard 3 mm bleed when the user requests a small bleed and no other measurement is given.
- Explain when an image is printable but likely to look soft at the requested size.
- Distinguish real source detail from interpolated resolution. A nominal 300 dpi export does not recreate missing detail.
- Preserve exact visual content. Do not use generative enhancement for operational photographs, logos, equipment, or existing lettering unless the user explicitly accepts possible reconstruction.
- If authorized, use conservative non-generative enlargement and light sharpening.
- Never upload files containing the sensitive personal or identification information prohibited by MBE's upload consent.

Keep the original file unchanged. Save final print-ready PDFs under `output/pdf/` when working in this workspace.

### 3. Draft conversational instructions

Write the request as a short note a person would naturally send. Avoid mechanical production-language lists when a sentence is clearer.

Use this pattern and adapt every detail:

```text
Hi MBE West End team,

Could I please get [quantity and job] printed [specifications] and [finishing]? [Bleed, trimming, or paper-stock details.]

I'll [collect/delivery details] and, if possible, would love to have it ready [date]. Please let me know the price and confirm when it will be ready.

Thanks,
Peter
```

### 4. Complete the upload form

Use the Browser and open the West End-specific upload URL.

1. Confirm QLD and MBE West End are selected.
2. Enter the customer details.
3. Enter the conversational instructions.
4. Verify the file contains no prohibited sensitive information.
5. Check the upload-consent box.
6. Upload the verified final file.
7. Wait until the upload reaches 100%.
8. Confirm the `Send Your Files` button is enabled.

The form accepts up to five files and 500 MB per file, including PDF, JPG, PNG, Word, AI, EPS, GIF, and ZIP.

### 5. Confirm before submission

Before clicking `Send Your Files`, show the user:

- Recipient centre
- Contact details being transmitted
- Attached filename
- Complete production specifications
- Collection or delivery details
- Requested date

Ask for explicit confirmation immediately before submission. Do not treat approval of the artwork or earlier workflow steps as approval to send the form.

If a CAPTCHA appears, ask the user to solve it. Do not bypass it.

### 6. Submit and verify

After confirmation:

1. Click `Send Your Files` once.
2. Verify the visible success page states `Thank You - File Uploaded Accepted` or `Your File Upload Has Been Accepted`.
3. Report successful submission and remind the user that MBE will reply with price and readiness confirmation.

Do not claim success based only on a click or unchanged form state.
