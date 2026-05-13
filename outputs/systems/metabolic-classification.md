# Metabolic Classification System
**The Evolved All Female Personal Training & Gym**
**Last Updated:** 2026-05-06 (split from strength-assessment-metabolic.md)

---

## Overview

The Metabolic Classification System is a scored survey (15 questions, each weighted) that classifies a prospect's metabolic type as Class A, B, or C. It functions as a **lead magnet and nurture tool** — delivered via the 30DNNC (30 Days No Nonsense Challenge) email sequences — and as a **retention pathway** for cancelling members (MC: Results/Value reason).

It is **not currently attached to a conversion mechanism** as a standalone funnel. The classification is offered contextually inside 30DNNC sequences and the cancellation retention path. A dedicated Women Over 40 — Metabolic Reboot workflow exists in draft but is not yet published.

---

## Forms & Surveys

### Metabolic Classification Form
**Survey ID:** `3dC0KGX0gwEjkDf5YZHx`

A 15-question scored survey. Produces a numeric score stored in `Metabolic Classification Score` which maps to Class A, B, or C.

**Direct link (custom value):** `{{ custom_values.metabolic_classification_assessment_link }}` → `https://api.leadconnectorhq.com/widget/survey/3dC0KGX0gwEjkDf5YZHx`

---

## Custom Fields — Metabolic Classification (Field Group `d5MFIbXvk4dTXJ0S2kwD`)

| Field | Type | Key | ID |
|---|---|---|---|
| Metabolic Classification Score | NUMERICAL | `contact.score_metabolic_classification_score` | `6SQirWtVQGGSo7W6HklT` |
| Q1. Whether you wish to gain or lose weight | RADIO | `contact.1_whether_you_wish_to_gain_or_lose_weight` | `VrQDMPYspbp9AAvNN5Qb` |
| Q2. Age influence on metabolism | RADIO | `contact.2_yes_its_true_age_does_influence_metabol` | `Z7OBrGmrtAGrTeBFwzHI` |
| Q3. Population/genetic background | RADIO | `contact.3_from_research_its_clear_that_some_popul` | `i18IGzbd5SOzvEsZkJRP` |
| Q4. How many diets have you been on? | RADIO | `contact.4_how_many_diets_have_you_been_on` | `xfqo5tRDetZPtWY3tdWX` |
| Q5. Breakfast habits | RADIO | `contact.5_breakfast_is_a_powerful_trigger_that_ca` | `xZ9IS72OCk2UqHbb0JaR` |
| Q6. Past 6 months meal structure (CHECKBOX) | CHECKBOX | `contact.6_for_the_past_6_months_pick_the_statemen` | `92uxbyv6ge8Ard6cOiKD` |
| Q6 (alt). Current eating description (RADIO) | RADIO | `contact.6_right_now_what_description_best_describ` | `C3xZccZrxS2zxREsU0Fg` |
| Q7. Structured 12-week body transformation history | RADIO | `contact.7_how_many_structured_12_week_body_transf` | `O4lrkKe2PEZThlfVKP2n` |
| Q8. Omega 3 knowledge | RADIO | `contact.8_a_high_ratio_of_omega_3_is_essential_fo` | `FT3Jy5fXkhCcgxSt1z02` |
| Q9. Resistance exercise history | RADIO | `contact.9_with_every_passing_decade_adults_lose_t` | `ZttqTyzvgfMwhzG5E0tj` |
| Q10. Aerobic exercise frequency | RADIO | `contact.10_how_often_do_you_perform_aerobic_type_` | `Cf6KvIgf26qjJGYSjj8U` |
| Q11. Body fat level | RADIO | `contact.11_how_much_body_fat_you_have_and_how_lon` | `g9MR18aAMemCQoc7Otfm` |
| Q12. Body fat storage pattern | RADIO | `contact.12_where_you_store_your_body_fat_has_impo` | `ZFgG35JN5T02j94tRuZK` |
| Q13. Sleep quality | CHECKBOX | `contact.13_sleep_quality_has_a_profound_effect_on` | `Y1SolIU7VWbatXBSejpl` |
| Q14. Metabolic blockers | CHECKBOX | `contact.14_metabolic_blockers_are_poor_sleep_habi` | `KZG1ydSgLgVnp3ivCGOP` |
| Q15. Mirror/body confidence | RADIO | `contact.15_when_you_stand_in_front_of_the_mirror_` | `02Ed49bwNfKCFRDZrVzp` |

> **Q6 duplication:** Two Q6 variants exist (CHECKBOX and RADIO, different keys) — likely different form versions. Scoring logic may be affected if both are active simultaneously.

> **Q14 duplicate:** A legacy variant (`contact.checkbox_8i12`, ID: `e0Ex3myyRqm6QiEcXgOG`) exists with near-identical options.

---

## Tags

| Tag | Meaning |
|---|---|
| `metabolic classification` | Completed or been sent the Metabolic Classification form |
| `metabolic blueprint` | Enrolled in the Metabolic Blueprint email sequence |
| `met class: a` | Classified as Metabolic Class A (highest metabolic efficiency) |
| `met class: b` | Classified as Metabolic Class B (moderate) |
| `met class: c` | Classified as Metabolic Class C (most challenged / most to gain) |
| `met class a` | Duplicate variant tag — inconsistent naming; both forms appear in tag list |

---

## Flow Diagrams

### Flow 1: 30DNNC → Metabolic Classification → Nurture → Offer

```
Lead enters via 30DNNC opt-in form (segmented by life stage)
    │
    ├── 20/30s       → 20/30 30DNNC workflow
    ├── Peri Menopause  → PERIM 30DNNC workflow
    ├── Post Menopause  → POSTM 30DNNC workflow
    ├── Planning Pregnancy → PPP 30DNNC workflow
    └── Teen         → TEEN 30DNNC workflow
    │
    ▼
[COLD] Marketing Pipeline: Signed Up | 30DNNC
    │
    ▼
Email sequence delivered (engagement tracked: 25%/50%/75%/100% open)
Tag: metabolic classification (applied when form link is sent/clicked)
    │
    ▼
Metabolic Classification Form completed (Survey ID: 3dC0KGX0gwEjkDf5YZHx)
    ├── 15 questions scored
    └── Score stored: Metabolic Classification Score (numerical)
    │
    ▼
Workflow: Metabolic Classification Form fires
Workflow: Metabolic Classification (Leads) fires
    │
    ▼
Score calculated → Class assigned
    ├── Class A → tag: met class: a
    ├── Class B → tag: met class: b
    └── Class C → tag: met class: c
    │
    ▼
Workflow: Metabolic Blueprint fires (personalised email sequence based on class)
    │
    ▼
Workflow: Metabolic Blueprint (END) fires
    │
    ▼
Offer: Strength & Longevity Assessment booking
    └── Custom value: {{ custom_values.strength__longevity_assessment }}
    │
    ▼
If Peri/Post Menopause: 7 Day Reset product offered
    ├── PERIM: 7 Day Reset Purchase workflow
    └── POSTM: 7 Day Reset Purchase workflow
```

---

### Flow 2: Metabolic Classification as Cancellation Retention Offer

```
Member cancellation reason: "Not seeing the results or value I expected"
    │
    ▼
MC: Results/Value workflow fires
    │
    ▼
Field: CS: Metabolic Interest - Continue Cancel
    └── If member does NOT decline → Metabolic Blueprint presented as retention offer
    │
    ▼
Tag: metabolic blueprint applied
Workflow: Metabolic Blueprint fires for existing member
```

---

### Flow 3: Women Over 40 — Metabolic Reboot (draft, not yet active)

```
Target: women 45+ (perimenopause / postmenopause / fit over 40 tags)
    │
    ▼
Workflow: Women Over 40 - Metabolic Reboot (draft — not published)
    │
    ▼
[Intent: deliver Metabolic Classification + personalised "reboot" content
targeting hormonal metabolic changes for this demographic]
```

---

## Custom Values

| Name | Key | Value |
|---|---|---|
| Metabolic Classification Assessment Link | `{{ custom_values.metabolic_classification_assessment_link }}` | `https://api.leadconnectorhq.com/widget/survey/3dC0KGX0gwEjkDf5YZHx` |
| Peri Menopause: 7 Day Reset | `{{ custom_values.peri_menopause_7_day_reset }}` | Google Storage URL (PDF/resource) |
| Post Menopause: 7 Day Reset | `{{ custom_values.post_menopause_7_day_reset }}` | Google Storage URL (PDF/resource) |

---

## System Notes

### What's working well
- **30DNNC segmentation by life stage** is sophisticated — separate tracks for teen, 20/30s, planning pregnancy, perimenopause, and postmenopause, each with organic and paid variants
- **Metabolic Blueprint as a retention offer** (inside MC: Results/Value cancellation pathway) repurposes a lead-gen asset as a retention tool
- **Tag taxonomy** (`met class: a/b/c`) enables list segmentation for offer personalisation

### Current gaps / things to review
- **Women Over 40 — Metabolic Reboot workflow is in draft** — core demographic but not yet published
- **Duplicate Q6 fields** — CHECKBOX and RADIO variants with different keys; scoring logic risk
- **Duplicate metabolic class tags** — `met class a` and `met class: a` both exist; workflows filtering on one miss contacts tagged with the other
- **Scoring logic not documented** — the mapping from question answers to score, and from score to Class A/B/C, is not captured in GHL. Lives in workflow logic or externally
- **No active standalone conversion mechanism** — the system currently feeds into the SA booking offer at the end of the Metabolic Blueprint sequence, but is not a standalone sales funnel
