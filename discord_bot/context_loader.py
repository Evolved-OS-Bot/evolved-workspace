"""
context_loader.py
Reads workspace context files and builds the system prompt
injected into every Claude API call.
"""

from pathlib import Path

WORKSPACE_ROOT = Path(__file__).parent.parent
CONTEXT_DIR    = WORKSPACE_ROOT / "context"

CONTEXT_FILES = [
    "business-info.md",
    "personal-info.md",
    "strategy.md",
    "current-data.md",
]


def load_journal_entries(max_entries=5):
    """Load the most recent daily journal entries."""
    journal_dir = CONTEXT_DIR / "journal"
    if not journal_dir.exists():
        return ""
    entries = sorted(journal_dir.glob("*.md"), reverse=True)[:max_entries]
    if not entries:
        return ""
    content = "\n\n---\n\n".join(f.read_text() for f in entries)
    return f"\n\n## Recent Journal Entries (last {len(entries)} days)\n\n{content}"


def build_system_prompt():
    """
    Reads all context files and journal entries,
    returns a complete system prompt string.
    """
    parts = [
        "You are Claude — a strategic advisor embedded in Peter Brown's Evolved OS workspace.",
        "You have full context about his business, role, strategy, and current KPI data.",
        "Be direct, concise, and strategically sharp. Challenge assumptions when warranted.",
        "Peter is accessing you via Discord on mobile — keep responses focused and scannable.",
        "Use markdown formatting where it helps readability.",
        "",
    ]

    for filename in CONTEXT_FILES:
        path = CONTEXT_DIR / filename
        if path.exists():
            parts.append(f"## {filename}\n\n{path.read_text().strip()}")

    parts.append(load_journal_entries())

    return "\n\n".join(filter(None, parts))
