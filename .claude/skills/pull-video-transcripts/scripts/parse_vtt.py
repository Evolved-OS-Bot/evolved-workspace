#!/usr/bin/env python3
"""
Parse a VTT caption file to clean plain text.
Usage: python3 parse_vtt.py <path-to-vtt-file>
"""
import re
import sys


def parse_vtt(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        text = f.read()

    lines = text.split("\n")
    result = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line == "WEBVTT":
            continue
        if line.startswith("Kind:") or line.startswith("Language:"):
            continue
        if re.match(r"^\d+$", line):
            continue
        if re.match(r"[\d:\.]+\s*-->\s*[\d:\.]+", line):
            continue
        # Strip inline VTT tags (<c>, <b>, timestamps, etc.)
        line = re.sub(r"<[^>]+>", "", line)
        line = line.strip()
        if line:
            result.append(line)

    # Deduplicate consecutive identical lines (auto-captions repeat heavily)
    deduped = []
    for line in result:
        if not deduped or line != deduped[-1]:
            deduped.append(line)

    return " ".join(deduped)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: parse_vtt.py <path-to-vtt-file>")
        sys.exit(1)
    print(parse_vtt(sys.argv[1]))
