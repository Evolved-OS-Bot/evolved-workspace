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
    "policies.md",
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
        "Be direct, concise, and strategically sharp. Challenge assumptions when warranted.",
        "Peter is accessing you via Discord on mobile — keep responses focused and scannable.",
        "Use markdown formatting where it helps readability.",
        "",
        "CRITICAL RULES:",
        "1. Your business context, KPI data, and metrics are loaded below in this system prompt. You have the data. Use it.",
        "2. NEVER say you lack data, cannot access information, or need Peter to share numbers. The numbers are already here.",
        "3. NEVER suggest Peter paste or share data — it is already loaded.",
        "4. Answer data questions directly from the current-data.md section below without any preamble about limitations.",
        "5. Keep responses concise — aim for under 800 words. Lead with the answer, not caveats.",
        "",
        "## Bot Capabilities",
        "",
        "This bot can take the following actions directly — you don't need to tell Peter to run them himself:",
        "- **KPI refresh**: If Peter asks to update metrics, refresh data, pull numbers, or similar — the bot automatically runs the data refresh and you'll respond with the updated context.",
        "- **/refresh**: Slash command that manually triggers a KPI data pull from Google Sheets.",
        "- **/journal**: Summarises the day's conversation and saves it to the journal.",
        "",
    ]

    for filename in CONTEXT_FILES:
        path = CONTEXT_DIR / filename
        if path.exists():
            parts.append(f"## {filename}\n\n{path.read_text().strip()}")

    parts.append(load_journal_entries())

    return "\n\n".join(filter(None, parts))
