from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import uuid
from pathlib import Path
from typing import BinaryIO


REQUIRED_FILES = {
    "reconciliation.sqlite": {"runs", "trainerize_clients"},
    "longitudinal.sqlite": {"daily_workouts", "exercise_results"},
    "assessments.sqlite": {
        "assessments",
        "assessment_exercises",
        "assessment_body_weights",
    },
}


def _digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def _copy_stream(source: BinaryIO, target: Path) -> None:
    with target.open("wb") as handle:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            handle.write(chunk)
    target.chmod(0o600)


def _validate_database(path: Path, required_tables: set[str]) -> None:
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    tables = {
        str(row[0])
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    connection.close()
    if integrity != "ok":
        raise ValueError(f"{path.name} failed SQLite integrity validation")
    missing = required_tables - tables
    if missing:
        raise ValueError(
            f"{path.name} is missing required tables: {sorted(missing)}"
        )


def install_bundle(
    data_dir: Path,
    manifest_stream: BinaryIO,
    file_streams: dict[str, BinaryIO],
) -> dict:
    try:
        manifest = json.load(manifest_stream)
    except (TypeError, ValueError) as exc:
        raise ValueError("manifest.json is not valid JSON") from exc
    if manifest.get("schema_version") != 1:
        raise ValueError("unsupported performance bundle schema")
    manifest_files = manifest.get("files")
    if not isinstance(manifest_files, dict):
        raise ValueError("bundle manifest files are missing")
    if set(file_streams) != set(REQUIRED_FILES):
        raise ValueError("bundle does not contain the required databases")

    data_dir.mkdir(parents=True, exist_ok=True)
    data_dir.chmod(0o700)
    temporary = data_dir / f".upload-{uuid.uuid4().hex}"
    temporary.mkdir(mode=0o700)
    try:
        for name, stream in file_streams.items():
            target = temporary / name
            _copy_stream(stream, target)
            expected = manifest_files.get(name) or {}
            if target.stat().st_size != int(expected.get("bytes") or -1):
                raise ValueError(f"{name} size does not match manifest")
            if _digest(target) != str(expected.get("sha256") or ""):
                raise ValueError(f"{name} checksum does not match manifest")
            _validate_database(target, REQUIRED_FILES[name])

        for name in REQUIRED_FILES:
            os.replace(temporary / name, data_dir / name)
        (data_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (data_dir / "manifest.json").chmod(0o600)
    finally:
        for path in temporary.glob("*"):
            path.unlink(missing_ok=True)
        temporary.rmdir()
    return {
        "status": "accepted",
        "runId": manifest.get("run_id"),
        "activeRoster": manifest.get("active_roster"),
        "latestWorkoutDate": manifest.get("latest_workout_date"),
        "generatedAt": manifest.get("generated_at"),
    }
