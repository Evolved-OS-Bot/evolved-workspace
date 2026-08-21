#!/usr/bin/env python3
"""Regenerate trainer portal quiz CSVs and HTML quiz blocks from Markdown."""

from __future__ import annotations

import csv
import html
import re
from pathlib import Path

from audit_trainer_portal import HTML_DIR, PORTAL, QUIZ_DIR, markdown_questions


CSV_FIELDS = [
    "Question ID ( Mandatory )",
    "Question ( Mandatory )",
    "Question Type ( Mandatory )",
    "Option A ( Optional )",
    "Option B ( Optional )",
    "Option C ( Optional )",
    "Option D ( Optional )",
    "Correct Answer ( Optional )",
    "Explanation ( Optional )",
]


def quiz_title(markdown: str) -> str:
    match = re.search(r"^## Quiz:\s*(.+)$", markdown, re.MULTILINE)
    if not match:
        raise ValueError("Markdown has no quiz heading")
    return re.sub(r"\s+\(\d+ Questions?\)\s*$", "", match.group(1)).strip()


def write_csv(path: Path, questions) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for question in questions:
            writer.writerow(
                {
                    "Question ID ( Mandatory )": question.number,
                    "Question ( Mandatory )": question.text,
                    "Question Type ( Mandatory )": "Single Choice",
                    "Option A ( Optional )": question.options.get("A", ""),
                    "Option B ( Optional )": question.options.get("B", ""),
                    "Option C ( Optional )": question.options.get("C", ""),
                    "Option D ( Optional )": question.options.get("D", ""),
                    "Correct Answer ( Optional )": question.correct,
                    "Explanation ( Optional )": "",
                }
            )


def render_html_quiz(title: str, questions) -> str:
    lines = [
        f"<!-- ===== QUIZ: {html.escape(title)} ({len(questions)} Questions) ===== -->",
        f"<h2>Quiz: {html.escape(title)}</h2>",
        "",
    ]
    for question in questions:
        lines.extend(
            [
                f"<p><strong>Q{question.number}:</strong> "
                f"{html.escape(question.text)}</p>",
                "<ul>",
            ]
        )
        for label in "ABCD":
            option = question.options.get(label, "")
            lines.append(f"  <li>{label}) {html.escape(option)}</li>")
        lines.extend(["</ul>", ""])
    return "\n".join(lines).rstrip() + "\n"


def replace_html_quiz(path: Path, rendered_quiz: str) -> None:
    text = path.read_text(encoding="utf-8")
    start = text.find("<!-- ===== QUIZ:")
    if start < 0:
        raise ValueError(f"{path} has no HTML quiz marker")

    assignment_start = text.find("<!-- ===== ASSIGNMENT", start)
    end = assignment_start if assignment_start >= 0 else len(text)
    suffix = text[end:].lstrip("\n")
    replacement = rendered_quiz
    if suffix:
        replacement += "\n\n" + suffix
    path.write_text(text[:start] + replacement, encoding="utf-8")


def main() -> None:
    course_files = sorted(PORTAL.glob("[0-9][0-9]-*.md"))
    updated = 0

    for markdown_path in course_files:
        if markdown_path.name in {"00-build-guide.md", "14-congratulations.md"}:
            continue

        markdown = markdown_path.read_text(encoding="utf-8")
        declared, questions = markdown_questions(markdown)
        if not questions:
            continue
        if declared != len(questions):
            raise ValueError(
                f"{markdown_path.name} declares {declared} questions "
                f"but contains {len(questions)}"
            )
        if any(not question.correct for question in questions):
            raise ValueError(f"{markdown_path.name} has a question with no correct answer")

        stem = markdown_path.stem
        write_csv(QUIZ_DIR / f"{stem}.csv", questions)
        replace_html_quiz(
            HTML_DIR / f"{stem}.html",
            render_html_quiz(quiz_title(markdown), questions),
        )
        updated += 1

    print(f"Regenerated quiz CSV and HTML quiz blocks for {updated} courses.")


if __name__ == "__main__":
    main()
