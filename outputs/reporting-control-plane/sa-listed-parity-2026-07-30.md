# Strength Assessment Listed-Metric Parity

**Run date:** 30 July 2026  
**Railway deployment:** `9d685d10-dafb-4dfc-a574-483c48cd7074`  
**Mode:** Protected shadow  
**Publication authority:** None  
**Workbook writes:** None

## Result

| Period | Workbook show rate | Governed listed show rate | Explained difference | Workbook conversion | Governed listed conversion | Result |
|---|---:|---:|---|---:|---:|---|
| 20–26 Jul | 2/5, 40.00% | 2/4, 50.00% | One blank attendance row | 2/2, 100.00% | 2/2, 100.00% | Passed |
| 2–29 Jul | 13/27, 48.15% | 13/22, 59.09% | Five blank attendance rows | 10/13, 76.92% | 10/13, 76.92% | Passed |
| 1 May–29 Jul | 54/78, 69.23% | 54/73, 73.97% | Five blank attendance rows | 34/54, 62.96% | 34/54, 62.96% | Passed |

Every conversion comparison is an exact match. Every show-rate difference is fully explained by the workbook counting blank attendance cells as bookings that did not show, while Reporting V2 only divides explicit `Y` by explicit `Y` plus `N`.

The hub stores these as passed parallel results with zero unexplained events. The show-rate differences are classified `legacy_defect`; conversion is classified `exact_match`.

## Five completed blank-attendance rows

| Appointments row | Person | Appointment | Convert? | Read-only GHL finding |
|---:|---|---|---|---|
| 228 | Julia Chen | 9 Jul 2026, 3:00 pm | blank | Exact calendar event corroborated; still Confirmed |
| 238 | Jade Wright | 20 Jul 2026, 12:15 pm | Y | Exact calendar event corroborated; still Confirmed |
| 244 | Vaishnavi Vakacharla | 28 Jul 2026, 7:30 am | Y | Exact calendar event corroborated; still Confirmed |
| 247 | Jody Austin | 29 Jul 2026, 12:00 pm | blank | No matching event in the active Strength Assessment calendar |
| 249 | Indie Cevallos | 29 Jul 2026, 4:00 pm | blank | Exact calendar event corroborated; still Confirmed |

`Confirmed` does not prove attendance. The two conversion rows remain in the approved listed-conversion numerator, but no blank row is silently promoted to `Showed`.

## Cutover position

- Listed conversion has passed parity for all three periods.
- Listed show rate has passed the explainability gate but is not an exact match because the workbook denominator is defective.
- Do not change the workbook.
- Do not infer attendance from GHL `Confirmed`.
- The recommended dashboard rule is the governed denominator: explicit `Y` divided by explicit `Y` plus `N`, with blank outcomes displayed separately.
- Dashboard publication still requires Peter Brown to accept the explained definition change.
