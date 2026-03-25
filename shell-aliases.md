# Shell Aliases for Claude Code

Two shell aliases streamline launching Claude Code sessions with this workspace.

## Setup

Add these lines to your `~/.zshrc` (or `~/.bashrc`):

```bash
alias cs='claude "/prime"'
alias cr='claude --dangerously-skip-permissions "/prime"'
```

Then reload your shell: `source ~/.zshrc`

## The Aliases

### `cs` — Claude Safe

```bash
alias cs='claude "/prime"'
```

Launches Claude Code and immediately runs `/prime` to load workspace context. Claude will ask for permission before executing commands, reading sensitive files, or making changes.

**Use when:** Starting a new session where you want to review and approve each action.

### `cr` — Claude Run

```bash
alias cr='claude --dangerously-skip-permissions "/prime"'
```

Launches Claude Code with permission prompts disabled, then runs `/prime`. Claude can execute commands and make changes without asking for approval.

**Use when:** You trust the task, want faster iteration, or are doing routine work where constant approvals slow you down.

### `update-metrics` — Refresh Live Business Data

```bash
alias update-metrics='cd ~/Downloads/claude-workspace-evolved && python3 scripts/update_metrics.py'
```

Reads the current week's column from the Google Sheet KPI tracker and rewrites `context/current-data.md`. Run this before starting a session to ensure Claude has current numbers during `/prime`.

**Dry run (prints output, does not write file):**
```bash
python3 scripts/update_metrics.py --dry-run
```

**Use when:** Starting a new session where you want Claude to have live KPI data, or after entering Cash Collected and Ad Spend in the sheet each week.

---

## Why Both?

- **`cs`** gives you oversight — good for unfamiliar tasks, sensitive operations, or when you want to learn what Claude is doing
- **`cr`** gives you speed — good for familiar workflows where you trust Claude to operate autonomously

Both run `/prime` automatically so Claude starts every session fully oriented to your workspace, goals, and context.
