from pathlib import Path


def test_ghl_client_has_no_mutation_requests():
    source = (Path(__file__).parents[1] / "ghl_client.py").read_text()
    forbidden = [".post(", ".put(", ".patch(", ".delete("]
    assert all(token not in source for token in forbidden)


def test_shadow_mode_is_mandatory(monkeypatch):
    from pt_booking_shadow.config import Settings

    monkeypatch.setenv("SHADOW_MODE", "false")
    try:
        Settings.from_env(require_runtime=False)
    except RuntimeError as exc:
        assert "SHADOW_MODE=true" in str(exc)
    else:
        raise AssertionError("Settings should fail closed when shadow mode is false")
