#!/usr/bin/env python3
"""Create or delete controlled GHL contacts for SA rebook guard tests."""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
GHL_BASE_URL = "https://services.leadconnectorhq.com"
TEST_CONTACTS = (
    ("member", "SA Guard Member", "member"),
    (
        "completed",
        "SA Guard Completed",
        "strength assessment showed",
    ),
)
WORKFLOW_IDS = {
    "no_show": "c531cc51-65cf-4a75-b4bf-ada7358a515a",
    "cancelled": "d6259817-fa44-43d1-bcbe-5f74e78f409f",
}


def load_local_env() -> None:
    env_path = Path(__file__).with_name(".env")
    for line in env_path.read_text().splitlines():
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {os.environ['GHL_API_KEY']}",
        "Version": "2021-07-28",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def create_contacts() -> Path:
    location_id = os.environ["GHL_LOCATION_ID"]
    created = []
    unique = str(time.time_ns())
    try:
        for kind, first_name, tag in TEST_CONTACTS:
            response = requests.post(
                f"{GHL_BASE_URL}/contacts/",
                headers=headers(),
                json={
                    "locationId": location_id,
                    "firstName": first_name,
                    "lastName": "Controlled Test",
                    "email": f"sa-rebook-{kind}-{unique}@example.invalid",
                    "tags": [tag],
                },
                timeout=30,
            )
            response.raise_for_status()
            contact_id = response.json()["contact"]["id"]
            readback = requests.get(
                f"{GHL_BASE_URL}/contacts/{contact_id}",
                headers=headers(),
                timeout=30,
            )
            readback.raise_for_status()
            contact = readback.json()["contact"]
            if tag not in set(contact.get("tags") or []):
                raise RuntimeError(f"{kind} test tag did not read back")
            created.append(
                {
                    "kind": kind,
                    "contact_id": contact_id,
                    "name": f"{first_name} Controlled Test",
                    "email": contact["email"],
                    "tag": tag,
                }
            )
    except Exception:
        for contact in created:
            requests.delete(
                f"{GHL_BASE_URL}/contacts/{contact['contact_id']}",
                headers=headers(),
                timeout=30,
            )
        raise

    generated_at = datetime.now(UTC)
    manifest = {
        "generated_at": generated_at.isoformat(),
        "purpose": "sa-rebook-guard-controlled-test",
        "contacts": created,
    }
    private_dir = ROOT / "data" / "private" / "strength-assessments"
    private_dir.mkdir(parents=True, exist_ok=True)
    path = private_dir / (
        "sa-rebook-guard-test-contacts-"
        f"{generated_at.strftime('%Y%m%dT%H%M%SZ')}.json"
    )
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return path


def delete_contacts(path: Path) -> None:
    manifest = json.loads(path.read_text())
    results = []
    for contact in manifest["contacts"]:
        response = requests.delete(
            f"{GHL_BASE_URL}/contacts/{contact['contact_id']}",
            headers=headers(),
            timeout=30,
        )
        results.append(
            {
                "kind": contact["kind"],
                "contact_id": contact["contact_id"],
                "deleted": response.ok,
                "status_code": response.status_code,
            }
        )
    if not all(result["deleted"] for result in results):
        raise RuntimeError(json.dumps(results, sort_keys=True))
    print(json.dumps({"deleted_contacts": results}, indent=2, sort_keys=True))


def enrol_contacts(path: Path, *, kind: str = "all") -> None:
    manifest = json.loads(path.read_text())
    results = []
    for contact in manifest["contacts"]:
        if kind != "all" and contact["kind"] != kind:
            continue
        for workflow_kind, workflow_id in WORKFLOW_IDS.items():
            response = requests.post(
                (
                    f"{GHL_BASE_URL}/contacts/{contact['contact_id']}"
                    f"/workflow/{workflow_id}"
                ),
                headers=headers(),
                json={},
                timeout=30,
            )
            response.raise_for_status()
            results.append(
                {
                    "contact_kind": contact["kind"],
                    "contact_id": contact["contact_id"],
                    "workflow_kind": workflow_kind,
                    "workflow_id": workflow_id,
                    "enrolled": True,
                    "status_code": response.status_code,
                }
            )
    print(json.dumps({"controlled_enrolments": results}, indent=2, sort_keys=True))


def prepare_customer_test(path: Path) -> None:
    manifest = json.loads(path.read_text())
    contact = next(
        item for item in manifest["contacts"] if item["kind"] == "member"
    )
    contact_id = contact["contact_id"]
    update = requests.put(
        f"{GHL_BASE_URL}/contacts/{contact_id}",
        headers=headers(),
        json={"type": "customer"},
        timeout=30,
    )
    update.raise_for_status()
    remove_tags = requests.delete(
        f"{GHL_BASE_URL}/contacts/{contact_id}/tags",
        headers=headers(),
        json={
            "tags": [
                "strength assessment no show",
                "strength assessment cancelled",
            ]
        },
        timeout=30,
    )
    remove_tags.raise_for_status()
    readback = requests.get(
        f"{GHL_BASE_URL}/contacts/{contact_id}",
        headers=headers(),
        timeout=30,
    )
    readback.raise_for_status()
    current = readback.json()["contact"]
    tags = set(current.get("tags") or [])
    if str(current.get("type") or "").lower() != "customer":
        raise RuntimeError("controlled contact type did not update to customer")
    if "member" not in tags:
        raise RuntimeError("controlled member tag was lost")
    if tags & {
        "strength assessment no show",
        "strength assessment cancelled",
    }:
        raise RuntimeError("incident tags were not removed")
    print(
        json.dumps(
            {
                "contact_id": contact_id,
                "contact_type": current.get("type"),
                "tags": sorted(tags),
            },
            indent=2,
            sort_keys=True,
        )
    )


def diagnose_tags() -> None:
    response = requests.get(
        f"{GHL_BASE_URL}/locations/{os.environ['GHL_LOCATION_ID']}/tags",
        headers=headers(),
        timeout=30,
    )
    response.raise_for_status()
    matches = [
        {"id": tag.get("id"), "name": tag.get("name")}
        for tag in response.json().get("tags", [])
        if str(tag.get("name") or "").strip().lower()
        in {"member", "strength assessment showed"}
    ]
    print(json.dumps({"matching_tags": matches}, indent=2, sort_keys=True))


def readback_contacts(path: Path) -> None:
    manifest = json.loads(path.read_text())
    results = []
    for contact in manifest["contacts"]:
        response = requests.get(
            f"{GHL_BASE_URL}/contacts/{contact['contact_id']}",
            headers=headers(),
            timeout=30,
        )
        response.raise_for_status()
        current = response.json()["contact"]
        results.append(
            {
                "kind": contact["kind"],
                "contact_id": contact["contact_id"],
                "tags": current.get("tags") or [],
            }
        )
    print(json.dumps({"contact_readback": results}, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("create")
    subparsers.add_parser("diagnose-tags")
    readback_parser = subparsers.add_parser("readback")
    readback_parser.add_argument("manifest", type=Path)
    enrol_parser = subparsers.add_parser("enrol")
    enrol_parser.add_argument("manifest", type=Path)
    enrol_parser.add_argument(
        "--kind",
        choices=("all", "member", "completed"),
        default="all",
    )
    prepare_parser = subparsers.add_parser("prepare-customer")
    prepare_parser.add_argument("manifest", type=Path)
    delete_parser = subparsers.add_parser("delete")
    delete_parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    load_local_env()
    if args.command == "create":
        path = create_contacts()
        print(path)
        print(path.read_text(), end="")
    elif args.command == "enrol":
        enrol_contacts(args.manifest, kind=args.kind)
    elif args.command == "prepare-customer":
        prepare_customer_test(args.manifest)
    elif args.command == "diagnose-tags":
        diagnose_tags()
    elif args.command == "readback":
        readback_contacts(args.manifest)
    else:
        delete_contacts(args.manifest)


if __name__ == "__main__":
    main()
