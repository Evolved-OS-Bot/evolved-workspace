#!/usr/bin/env python3
"""
test_formulas.py
Inserts known test data into raw tabs, reads back KPI formula results,
and verifies they match expected values.

Usage:
    python scripts/test_formulas.py           # Insert data + verify
    python scripts/test_formulas.py --cleanup # Remove test rows after
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv(Path(__file__).parent / ".env")

SCOPES       = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = os.environ.get("GOOGLE_SPREADSHEET_ID")
KPI_SHEET_NAME = os.environ.get("GOOGLE_KPI_SHEET_NAME", "KPI's The Evolved")
CLEANUP      = "--cleanup" in sys.argv

# ── Test week (current: 23 Mar 2026) ────────────────────────────────────────
W1        = "23/03/2026"
W2        = "24/03/2026"
W3        = "25/03/2026"
W4        = "26/03/2026"
NEXT_WEEK = "30/03/2026"   # outside week → should NOT be counted
LAST_WEEK = "16/03/2026"   # outside week → should NOT be counted

# ── Test data ────────────────────────────────────────────────────────────────
# Subscribes: A=Date, B=First, C=Last, D=Source, E=LeadMagnet, F=Mobile, G=Email
SUBSCRIBES = [
    [W1, "TEST", "Sub1", "organic | google",      "30DNNC", "", "t1@test.com"],
    [W2, "TEST", "Sub2", "organic | google",      "30DNNC", "", "t2@test.com"],
    [W3, "TEST", "Sub3", "organic | chatgpt.com", "30DNNC", "", "t3@test.com"],
    [W1, "TEST", "Sub4", "paid | facebook",       "30DNNC", "", "t4@test.com"],
    [W2, "TEST", "Sub5", "paid | facebook",       "30DNNC", "", "t5@test.com"],
]
# organic=3, paid=2, total=5

# Appointments: A=DateBooked, B=First, C=Last, D=LeadMagnet, E=Mobile, F=Email,
#               G=Source, H=ApptDate, I=Salesperson, J=PreQual?, K=Show?, L=Convert?
APPOINTMENTS = [
    # DateBooked in week, ApptDate in week — counts as both lead AND booking
    [W1, "TEST", "Appt1", "", "", "", "organic | google", W2,        "Megan Brown", "Y", "Y", "Y"],
    # DateBooked in week, ApptDate in week
    [W2, "TEST", "Appt2", "", "", "", "paid | facebook",  W3,        "Megan Brown", "N", "Y", "N"],
    # DateBooked in week, ApptDate NEXT week — counts as lead only
    [W3, "TEST", "Appt3", "", "", "", "organic | google", NEXT_WEEK, "Megan Brown", "Y", "N", "N"],
    # DateBooked LAST week, ApptDate in week — counts as booking only
    [LAST_WEEK, "TEST", "Appt4", "", "", "", "organic | google", W1, "Megan Brown", "N", "N", "N"],
]
# Leads (DateBooked in week):       Appt1, Appt2, Appt3 = 3
# Studio Bookings (ApptDate in week): Appt1, Appt2, Appt4 = 3
# Show Y (ApptDate in week):          Appt1, Appt2 = 2
# Pre-Qual Y (ApptDate in week):      Appt1 only = 1

# Sales: A=Date, B=First, C=Last, D=Mobile, E=Email, F=Source, G=Product, H=Salesperson, I=Cash
SALES = [
    [W1, "TEST", "Sale1", "", "", "organic | google", "Bronze",     "Megan Brown", "$99"],
    [W2, "TEST", "Sale2", "", "", "paid | facebook",  "Bronze",     "Megan Brown", "$99"],
    [W3, "TEST", "Sale3", "", "", "organic | google", "Silver",     "Megan Brown", "$149"],
    [W4, "TEST", "Sale4", "", "", "paid | google",    "PT 30M 4PK", "Beth Fry",    "$200"],
]
# SGPT via paid social:  Sale2 (Bronze+facebook)            = 1
# SGPT via google paid:  0
# SGPT via organic:      Sale1 (Bronze), Sale3 (Silver)     = 2
# SGPT total:            Sale1+Sale2+Sale3                  = 3
# PT via paid social:    0
# PT via google paid:    Sale4 (PT*+google)                 = 1
# PT via organic:        Sale3 (Silver+organic)             = 1
# PT total:              Sale3+Sale4                        = 2
# Sales via paid:        Sale2+Sale4                        = 2
# Sales via organic:     Sale1+Sale3                        = 2
# Sales total:           4

# SGPT Cancellations: A=DateSubmitted, B=First, C=Last
SGPT_CANCELS = [
    [W1, "TEST", "SGPTCancel1"],
]
# SGPT cancels: 1

# PT Cancellations: A=Date, B=First, C=Last, D=Mobile, E=Email, F=CancelPT
PT_CANCELS = [
    [W2, "TEST", "PTCancel1", "", "", ""],
]
# PT cancels: 1

# ── Expected KPI results ─────────────────────────────────────────────────────
EXPECTED = {
    33: (3,  "Organic subscribes"),
    34: (2,  "Paid subscribes"),
    35: (5,  "Total subscribes"),
    42: (3,  "Total leads (by date booked)"),
    52: (3,  "Total studio bookings (by appt date)"),
    57: (2,  "Studio bookings attended (Show=Y)"),
    59: (1,  "Pre-qualified (PreQual=Y)"),
    63: (1,  "SGPT sales via paid social"),
    64: (0,  "SGPT sales via google paid"),
    65: (2,  "SGPT sales via organic (website)"),
    69: (3,  "SGPT sales total"),
    70: (0,  "PT sales via paid social"),
    71: (1,  "PT sales via google paid"),
    72: (1,  "PT sales via organic (website)"),
    76: (2,  "PT sales total"),
    77: (2,  "Sales via paid"),
    78: (2,  "Sales via organic"),
    79: (4,  "Sales total"),
    89: (1,  "SGPT cancels"),
    90: (1,  "PT cancels"),
    93: (2,  "SGPT gained/lost (3-1)"),
    94: (1,  "PT gained/lost (2-1)"),
}


def get_service():
    creds_file = os.environ.get("GOOGLE_SHEETS_CREDENTIALS_FILE")
    creds = service_account.Credentials.from_service_account_file(
        creds_file, scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def get_sheet_ids(service):
    result = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    return {s["properties"]["title"]: s["properties"]["sheetId"]
            for s in result.get("sheets", [])}


def append_rows(service, sheet_name, rows):
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{sheet_name}'!A1",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": rows},
    ).execute()


def delete_test_rows(service, sheet_ids, sheet_name, first_name_col=1):
    """Delete rows where column B (first_name_col) = 'TEST'."""
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{sheet_name}'!A:B",
    ).execute()
    rows = result.get("values", [])
    delete_requests = []
    for i, row in reversed(list(enumerate(rows))):
        if len(row) > first_name_col and row[first_name_col] == "TEST":
            delete_requests.append({
                "deleteDimension": {
                    "range": {
                        "sheetId": sheet_ids[sheet_name],
                        "dimension": "ROWS",
                        "startIndex": i,
                        "endIndex": i + 1,
                    }
                }
            })
    if delete_requests:
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={"requests": delete_requests},
        ).execute()
        print(f"  Deleted {len(delete_requests)} test rows from '{sheet_name}'")
    else:
        print(f"  No test rows found in '{sheet_name}'")


def get_kpi_col(service):
    """Find current week column index in KPI tab row 1."""
    from datetime import date, datetime
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{KPI_SHEET_NAME}'!1:1",
    ).execute()
    header = result.get("values", [[]])[0]
    today = date.today()
    best_col, best_date = None, None
    for i, cell in enumerate(header):
        for fmt in ("%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d"):
            try:
                d = datetime.strptime(str(cell).strip(), fmt).date()
                if d <= today and (best_date is None or d > best_date):
                    best_date, best_col = d, i
                break
            except ValueError:
                continue
    return best_col, best_date


def col_letter(idx):
    s = ""
    n = idx + 1
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def main():
    service = get_service()
    sheet_ids = get_sheet_ids(service)

    if CLEANUP:
        print("Cleaning up test data...")
        delete_test_rows(service, sheet_ids, "Subscribes")
        delete_test_rows(service, sheet_ids, "Appointments")
        delete_test_rows(service, sheet_ids, "Sales")
        delete_test_rows(service, sheet_ids, "SGPT Cancellations")
        delete_test_rows(service, sheet_ids, "PT Cancellations")
        print("Done.")
        return

    # ── Read baseline before inserting ───────────────────────────────────
    col_idx, week_date = get_kpi_col(service)
    col = col_letter(col_idx)
    print(f"Reading baseline from column {col} (week of {week_date})...")

    def read_kpi_values():
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"'{KPI_SHEET_NAME}'!{col}1:{col}100",
            valueRenderOption="UNFORMATTED_VALUE",
        ).execute()
        return result.get("values", [])

    def get_val(values, row):
        try:
            v = values[row - 1][0] if row - 1 < len(values) and values[row - 1] else 0
            return int(float(v))
        except (IndexError, ValueError, TypeError):
            return 0

    baseline = read_kpi_values()
    baseline_counts = {row: get_val(baseline, row) for row in EXPECTED}
    print(f"Baseline captured. Existing data in current week: {baseline_counts.get(79, 0)} sales, {baseline_counts.get(35, 0)} subscribes\n")

    # ── Insert test data ─────────────────────────────────────────────────
    print("Inserting test data...")
    append_rows(service, "Subscribes",         SUBSCRIBES)
    append_rows(service, "Appointments",       APPOINTMENTS)
    append_rows(service, "Sales",              SALES)
    append_rows(service, "SGPT Cancellations", SGPT_CANCELS)
    append_rows(service, "PT Cancellations",   PT_CANCELS)
    print("Test data inserted. Waiting 3s for sheets to recalculate...")
    time.sleep(3)

    after = read_kpi_values()

    # ── Verify delta = expected additions ─────────────────────────────────
    passed = 0
    failed = 0
    print(f"{'Row':<5} {'Expected':<10} {'Delta':<10} {'Status':<8} Description")
    print("-" * 70)
    for row in sorted(EXPECTED.keys()):
        expected_addition, description = EXPECTED[row]
        before_val = baseline_counts[row]
        after_val  = get_val(after, row)
        delta      = after_val - before_val

        if delta == expected_addition:
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"
            failed += 1

        print(f"{row:<5} +{expected_addition:<9} +{delta:<9} {status:<8} {description}")

    print("-" * 70)
    print(f"\n{passed} passed, {failed} failed")
    if failed == 0:
        print("\nAll formulas working correctly.")
        print("Run with --cleanup to remove test data, then drag column AD formulas right for future weeks.")
    else:
        print("\nSome formulas failed. Check the KPI tab directly to investigate.")


if __name__ == "__main__":
    main()
