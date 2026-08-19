import pytest

from reporting_control import website_public_proof_job


def environment():
    return {
        "PUBLIC_PROOF_HUB_URL": "https://hub.example",
        "PUBLIC_PROOF_HUB_SECRET": "hub-secret",
        "PUBLIC_PROOF_WORDPRESS_URL": "https://site.example",
        "PUBLIC_PROOF_WORDPRESS_SECRET": "wp-secret",
    }


def test_job_requires_every_configuration_value():
    values = environment()
    del values["PUBLIC_PROOF_WORDPRESS_SECRET"]
    with pytest.raises(RuntimeError, match="PUBLIC_PROOF_WORDPRESS_SECRET"):
        website_public_proof_job.run_from_environment(values)


def test_job_uses_the_governed_hub_to_wordpress_publisher(monkeypatch):
    captured = {}

    def fake_publish(**kwargs):
        captured.update(kwargs)
        return {"status": "accepted", "snapshotId": "a" * 64}

    monkeypatch.setattr(
        website_public_proof_job,
        "publish_latest",
        fake_publish,
    )
    result = website_public_proof_job.run_from_environment(environment())
    assert result["status"] == "accepted"
    assert captured == {
        "hub_url": "https://hub.example",
        "hub_secret": "hub-secret",
        "wordpress_url": "https://site.example",
        "wordpress_secret": "wp-secret",
    }
