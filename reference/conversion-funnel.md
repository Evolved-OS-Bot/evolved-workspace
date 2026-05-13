# Conversion Funnel Strategy — The Evolved

**Last updated:** 2026-05-03

---

## Overarching Principle

**The Evolved is at capacity. Every new member enters through the waitlist.**

This is not a limitation to hide — it is a premium signal. Demand exceeds supply. The waitlist exists because the product is good enough to wait for. All copy, CTAs, and funnel architecture must reflect this reality consistently from the first touchpoint to the booking confirmation.

A visitor who lands on the homepage and clicks a CTA should never be surprised by what they find on the other side. The journey must feel inevitable, not jarring.

---

## The Conversion Flow

```
Homepage
  └── Pick Your Journey (life stage + goal selection)
        └── Life-stage landing page (one of 10)
              └── Waitlist form submission
                    └── GHL thank-you page
                          └── Strength Assessment calendar (book now)
                                └── [If no booking] Email re-engagement sequence
                                      └── SA booking page (go.theevolvedgym.com.au/strength-assessment)
```

Every step is intentional. No shortcuts bypass this sequence.

---

## The 10 Landing Pages

5 life stages × 2 traffic sources = 10 dedicated pages.

| Life Stage     | Organic URL                              | Paid URL                                 |
| -------------- | ---------------------------------------- | ---------------------------------------- |
| Teenager       | `/teen-30dnnc-o`                         | `/teen-30dnnc-p`                         |
| 20s – 30s      | `/20s30s-30dnnc-o`                       | `/20s30s-30dnnc-p`                       |
| Pregnancy      | `/pregnancy-30dnnc-o`                    | `/pregnancy-30dnnc-p`                    |
| Peri-Menopause | `/perimenopause-30dnnc-o`                | `/perimenopause-30dnnc-p`                |
| Post-Menopause | `/post-menopause-30dnnc-o`               | `/post-menopause-30dnnc-p`               |

**Paid traffic goes directly to `-p` pages via ad links — never via the homepage.**
The homepage is organic-only and always links to `-o` pages.

Each landing page has its own dedicated GHL form. Form identity (not URL params) triggers the correct intake workflow, which tags the lead with life stage and traffic source automatically.

---

## GHL Backend Architecture

Each of the 10 landing pages triggers its own workflow on form submission:

1. Internal notification
2. Update 'Lead Source' field
3. Wait 1 min
4. Add life-stage tag (e.g. `20/30s`)
5. Add traffic source tag (`organic` or `paid`)
6. Create spreadsheet row
7. Add to life-stage nurture workflow
8. Show thank-you page with Strength Assessment calendar

**The Strength Assessment booking page** (`go.theevolvedgym.com.au/strength-assessment`) is **only used in email re-engagement sequences** — for leads who submitted the waitlist form but did not book a calendar slot on the thank-you page. It is not linked from the homepage.

---

## CTA Copy Rules

### The rule: say what you mean

Every CTA must honestly describe the next step. Never imply direct booking when the next step is a waitlist form.

| State | CTA Text |
|---|---|
| Pre-selection (no life stage chosen) | "Join the Waitlist" |
| Post-selection (life stage + goal chosen) | "Join the [Stage] Waitlist →" |
| Mid-page waitlist blocks (pre-selection) | "Choose your stage to join the waitlist ↑" |
| Mid-page waitlist blocks (post-selection) | "Join the [Stage] Waitlist →" |
| Sticky profile bar (pre-selection) | "Join the Waitlist →" |
| Sticky profile bar (post-selection) | "Join the [Stage] List →" |
| PYJ confirmation panel CTA | "See the [Stage] path →" |
| Sarcopenia chart CTA | "See Where You Fall on This Curve" (contextual — leave as is) |

### What to avoid

- "Book Your Strength Assessment" as a homepage CTA — this implies immediate booking, which is not what happens. Reserve this phrase for the step *inside* the GHL thank-you page and in email sequences.
- Linking any homepage CTA directly to `go.theevolvedgym.com.au/strength-assessment`
- Any CTA that promises a direct transaction when a waitlist step comes first

### At-capacity framing

Lead with the waitlist as a feature, not an apology:

> "Currently at capacity — waitlist open"
> "We open a small number of spots each month"
> "Priority goes to women on our waitlist"

Not:

> "Sorry, we're full"
> "Unfortunately we can't take bookings right now"

---

## Homepage CTA Architecture

### Pre-selection state (no PYJ selection made)

All primary CTAs on the homepage anchor to `#pyj-section`. The visitor is guided to select their life stage before going anywhere. This ensures:
- They land on the right life-stage page
- The correct GHL workflow fires on form submission
- The lead is tagged correctly from day one

### Post-selection state (life stage + goal chosen via PYJ)

`rcUpdateCTALinks()` and `rcUpdateWaitlistCTAs()` both fire on every `refresh()` call. They update:
- Button `href` → correct organic landing page (`stage.url + ?goal=&decade=`)
- Button `textContent` → "Join the [Stage] Waitlist →"

All 10 primary CTAs and 4 mid-page waitlist blocks update simultaneously. The entire page reflects the visitor's selected profile.

---

## What Passes to the Landing Page

The organic landing page URL receives:
- `?goal=` — the goal ID selected in PYJ (e.g. `recomp`, `lose-weight`)
- `?decade=` — the life-stage decade (e.g. `40s`, `60s`)

These params are available for future GHL personalisation (conditional content blocks on the landing page reading `{{params.goal}}`). Currently GHL ignores them — form identity handles all tagging. Adding landing page personalisation based on these params is a future enhancement.

---

## Future Enhancements (not yet implemented)

1. **Landing page personalisation by goal** — GHL conditional content blocks reading `{{params.goal}}` to show a matched headline and member story on arrival (warm landing).
2. **SA booking page param consumption** — map `?goal=&decade=&stage=` to hidden fields so the SA pre-qual bot can skip intake questions for pre-identified visitors.
3. **Auto-select life stage from URL** — `?stage=perimenopause` on homepage URL auto-selects the PYJ stage for direct campaign linking.
