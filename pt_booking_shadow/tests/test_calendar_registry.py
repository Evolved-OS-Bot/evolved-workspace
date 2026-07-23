import pytest

from pt_booking_shadow.calendar_registry import build_registry


def _raw(trainer, duration):
    suffix = "Minute" if trainer == "Megan" and duration in {45, 60} else "Min"
    pt = "" if trainer == "Nora" else " PT"
    return {
        "id": f"{trainer}-{duration}",
        "name": f"{duration} {suffix} 1:1{pt} - {trainer}",
        "isActive": True,
        "slotDuration": duration,
        "teamMembers": [{"userId": f"user-{trainer}"}],
    }


def test_registry_accepts_all_live_name_variants():
    calendars = [
        _raw(trainer, duration)
        for trainer in ("Megan", "Piper", "Nora", "Katrina", "Leisa")
        for duration in (30, 45, 60)
    ]
    registry = build_registry(calendars)
    assert len(registry) == 15
    assert {(item.trainer, item.duration_minutes) for item in registry} == {
        (trainer, duration)
        for trainer in ("Megan", "Piper", "Nora", "Katrina", "Leisa")
        for duration in (30, 45, 60)
    }


def test_registry_fails_closed_when_calendar_missing():
    calendars = [
        _raw(trainer, duration)
        for trainer in ("Megan", "Piper", "Nora", "Katrina", "Leisa")
        for duration in (30, 45, 60)
    ][:-1]
    with pytest.raises(RuntimeError, match="Invalid live PT calendar registry"):
        build_registry(calendars)
