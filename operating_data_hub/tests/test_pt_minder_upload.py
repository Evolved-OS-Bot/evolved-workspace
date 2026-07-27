from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from upload_pt_minder_snapshot import build_payload


def test_csv_aliases_build_valid_pt_minder_payload(tmp_path):
    source = tmp_path / "ptminder.csv"
    source.write_text(
        "Client ID,Email,Status,Weekly Amount,Last Payment Date\n"
        "ptm-1,member@example.com,Active,120,2026-07-24\n",
        encoding="utf-8",
    )
    payload = build_payload(source)
    assert payload["rows"][0]["source_account_id"] == "ptm-1"
    assert payload["rows"][0]["amount"] == "120.00"

