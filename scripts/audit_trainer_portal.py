#!/usr/bin/env python3
"""Audit trainer portal Markdown, HTML, and quiz CSV consistency."""

from __future__ import annotations

import csv
import html
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PORTAL = ROOT / "outputs" / "trainer-portal"
HTML_DIR = PORTAL / "html"
QUIZ_DIR = PORTAL / "quiz-csvs"


@dataclass(frozen=True)
class Question:
    number: int
    text: str
    options: dict[str, str]
    correct: str


def normalise(value: str) -> str:
    value = html.unescape(value)
    value = re.sub(r"<[^>]+>", " ", value)
    value = value.replace("✓", " ")
    value = value.replace("’", "'").replace("“", '"').replace("”", '"')
    value = re.sub(r"[*_`]", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip().lower()


def markdown_questions(text: str) -> tuple[int | None, list[Question]]:
    quiz_match = re.search(
        r"^## Quiz:[^\n]*$([\s\S]*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE,
    )
    if not quiz_match:
        return None, []

    header = quiz_match.group(0).splitlines()[0]
    declared_match = re.search(r"\((\d+) Questions?\)\s*$", header)
    declared = int(declared_match.group(1)) if declared_match else None
    body = quiz_match.group(1)
    matches = list(re.finditer(r"^\*\*Q(\d+):\*\*\s*(.+)$", body, re.MULTILINE))
    questions: list[Question] = []

    for index, match in enumerate(matches):
        number = int(match.group(1))
        question_text = match.group(2).strip()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        block = body[match.end() : end]
        options: dict[str, str] = {}
        correct = ""

        for option_match in re.finditer(r"^- ([A-D])\)\s*(.+)$", block, re.MULTILINE):
            label = option_match.group(1)
            option = option_match.group(2).strip()
            if "✓" in option:
                correct = label
            options[label] = option.replace("✓", "").strip()

        questions.append(Question(number, question_text, options, correct))

    return declared, questions


def csv_questions(path: Path) -> list[Question]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))

    questions: list[Question] = []
    for row in rows:
        number = int(row["Question ID ( Mandatory )"])
        options = {
            label: row.get(f"Option {label} ( Optional )", "").strip()
            for label in "ABCD"
        }
        questions.append(
            Question(
                number=number,
                text=row["Question ( Mandatory )"].strip(),
                options=options,
                correct=row.get("Correct Answer ( Optional )", "").strip(),
            )
        )
    return questions


def html_questions(text: str) -> list[Question]:
    matches = list(
        re.finditer(
            r"<p>\s*<strong>Q(\d+):</strong>\s*(.*?)</p>",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
    )
    questions: list[Question] = []

    for index, match in enumerate(matches):
        number = int(match.group(1))
        question_text = normalise(match.group(2))
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[match.end() : end]
        options: dict[str, str] = {}

        for option_match in re.finditer(
            r"<li>\s*([A-D])\)\s*(.*?)</li>",
            block,
            flags=re.IGNORECASE | re.DOTALL,
        ):
            options[option_match.group(1).upper()] = normalise(option_match.group(2))

        questions.append(Question(number, question_text, options, ""))

    return questions


def lesson_titles_from_markdown(text: str) -> list[str]:
    return [
        match.group(1).strip()
        for match in re.finditer(r"^### Lesson \d+:\s*(.+)$", text, re.MULTILINE)
    ]


def h2_titles_from_html(text: str) -> list[str]:
    return [
        normalise(match.group(1))
        for match in re.finditer(r"<h2[^>]*>(.*?)</h2>", text, re.IGNORECASE | re.DOTALL)
    ]


def compare_question_sets(
    stem: str,
    source_name: str,
    expected: list[Question],
    actual: list[Question],
) -> list[str]:
    errors: list[str] = []
    if len(expected) != len(actual):
        errors.append(
            f"{stem}: {source_name} has {len(actual)} questions; Markdown has {len(expected)}"
        )

    actual_by_number = {question.number: question for question in actual}
    for expected_question in expected:
        actual_question = actual_by_number.get(expected_question.number)
        if not actual_question:
            errors.append(
                f"{stem}: {source_name} is missing Q{expected_question.number}"
            )
            continue

        if normalise(expected_question.text) != normalise(actual_question.text):
            errors.append(
                f"{stem}: {source_name} Q{expected_question.number} text differs"
            )

        if expected_question.options and actual_question.options:
            for label, expected_option in expected_question.options.items():
                actual_option = actual_question.options.get(label, "")
                if normalise(expected_option) != normalise(actual_option):
                    errors.append(
                        f"{stem}: {source_name} Q{expected_question.number} "
                        f"option {label} differs"
                    )

        if actual_question.correct and expected_question.correct != actual_question.correct:
            errors.append(
                f"{stem}: {source_name} Q{expected_question.number} correct answer "
                f"is {actual_question.correct}; Markdown says {expected_question.correct}"
            )

    return errors


def audit_course(markdown_path: Path) -> list[str]:
    stem = markdown_path.stem
    markdown = markdown_path.read_text(encoding="utf-8")
    html_path = HTML_DIR / f"{stem}.html"
    csv_path = QUIZ_DIR / f"{stem}.csv"
    errors: list[str] = []

    if not html_path.exists():
        return [f"{stem}: missing HTML file"]

    html_text = html_path.read_text(encoding="utf-8")
    lesson_titles = lesson_titles_from_markdown(markdown)
    html_h2_titles = h2_titles_from_html(html_text)

    for title in lesson_titles:
        if normalise(title) not in html_h2_titles:
            errors.append(f"{stem}: HTML is missing lesson heading '{title}'")

    declared, markdown_quiz = markdown_questions(markdown)
    if markdown_quiz:
        if declared is not None and declared != len(markdown_quiz):
            errors.append(
                f"{stem}: Markdown declares {declared} questions but contains "
                f"{len(markdown_quiz)}"
            )

        if not csv_path.exists():
            errors.append(f"{stem}: missing quiz CSV")
        else:
            errors.extend(
                compare_question_sets(
                    stem, "CSV", markdown_quiz, csv_questions(csv_path)
                )
            )

        errors.extend(
            compare_question_sets(
                stem, "HTML", markdown_quiz, html_questions(html_text)
            )
        )
    elif csv_path.exists():
        errors.append(f"{stem}: quiz CSV exists but Markdown has no quiz")

    return errors


def audit_practical_sign_off() -> list[str]:
    markdown_path = PORTAL / "13-practical-sign-off.md"
    html_path = HTML_DIR / "13-practical-sign-off.html"
    errors: list[str] = []

    if not markdown_path.exists() or not html_path.exists():
        return ["practical-sign-off: Markdown or HTML file is missing"]

    markdown = markdown_path.read_text(encoding="utf-8")
    html_text = html_path.read_text(encoding="utf-8")
    markdown_blocks = re.findall(r"^## Block (\d+):", markdown, re.MULTILINE)
    html_blocks = re.findall(r"<h2[^>]*>Block (\d+):", html_text, re.IGNORECASE)

    if markdown_blocks != html_blocks:
        errors.append(
            "practical-sign-off: Markdown and HTML block sequences differ "
            f"({markdown_blocks} vs {html_blocks})"
        )

    return errors


def main() -> int:
    course_files = sorted(
        path
        for path in PORTAL.glob("[0-9][0-9]-*.md")
        if path.name not in {"00-build-guide.md", "13-practical-sign-off.md"}
    )
    errors: list[str] = []

    for course_file in course_files:
        errors.extend(audit_course(course_file))
    errors.extend(audit_practical_sign_off())

    print(f"Audited {len(course_files)} numbered course files plus Practical Sign-Off.")
    if errors:
        print(f"Found {len(errors)} issue(s):")
        for error in errors:
            print(f"- {error}")
        return 1

    print("All Markdown, HTML, quiz CSV, assignment, and sign-off structure checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
