#!/usr/bin/env python3
"""Verify Trainerize credentials without printing client information."""

from trainerize_client import TrainerizeAPIError, TrainerizeClient


def main() -> int:
    try:
        total = TrainerizeClient().check_connection()
    except TrainerizeAPIError as exc:
        print(f"Trainerize connection failed: {exc}")
        return 1

    print(f"Trainerize connected successfully. Active clients: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
