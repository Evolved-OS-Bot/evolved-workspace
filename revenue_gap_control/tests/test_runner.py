from datetime import date

from scripts.run_revenue_gap_control import default_window


def test_monday_defaults_to_the_just_completed_service_week():
    assert default_window(date(2026, 7, 27)) == (
        date(2026, 7, 20),
        date(2026, 7, 26),
    )


def test_friday_defaults_to_the_current_service_week():
    assert default_window(date(2026, 7, 31)) == (
        date(2026, 7, 27),
        date(2026, 8, 2),
    )
