"""
journal.py
Generates a daily journal summary from the day's #evolved-os
conversation history and writes it to context/journal/YYYY-MM-DD.md.
"""

import anthropic
from datetime import date
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).parent.parent
JOURNAL_DIR    = WORKSPACE_ROOT / "context" / "journal"

JOURNAL_PROMPT = """\
You are summarising a day's strategic conversation between Peter Brown and his AI advisor.

Create a structured daily journal entry with:
1. **Date and headline** — one sentence capturing the day's main theme
2. **Key decisions made** — bulleted list of any decisions or directions chosen
3. **Key insights** — important realisations, patterns, or strategic observations
4. **Open items** — anything left unresolved or flagged for follow-up
5. **Metrics discussed** — any specific numbers or KPIs referenced
6. **Tone / context** — brief note on what Peter was focused on (e.g. growth, ops, a specific problem)

Be specific and factual. Use Peter's actual words where they capture intent clearly.
This entry will be read by Claude in future sessions as memory — make it dense and useful.
"""


def generate_journal_entry(conversation_history: list[dict]) -> str:
    """
    Takes the day's conversation history and generates a journal entry via Claude.
    Returns the formatted markdown string.
    """
    client = anthropic.Anthropic()

    messages = conversation_history + [
        {
            "role": "user",
            "content": "Please summarise today's conversation into a journal entry using the format specified.",
        }
    ]

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=JOURNAL_PROMPT,
        messages=messages,
    )

    today   = date.today().strftime("%Y-%m-%d")
    weekday = date.today().strftime("%A")
    entry   = response.content[0].text

    return f"# Journal — {today} ({weekday})\n\n{entry}\n"


def save_journal_entry(entry: str) -> Path:
    """Writes the journal entry to context/journal/YYYY-MM-DD.md."""
    JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
    today    = date.today().strftime("%Y-%m-%d")
    filepath = JOURNAL_DIR / f"{today}.md"
    filepath.write_text(entry)
    return filepath
