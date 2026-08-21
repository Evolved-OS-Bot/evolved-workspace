#!/usr/bin/env python3
"""
bot.py
Evolved OS Discord bot.
- #evolved-os: direct Claude chat with full workspace context
- /journal: summarises the day's conversation and posts to #daily-journal
"""

import asyncio
import json
import os
import subprocess
import sys
import datetime
import discord
import anthropic
from discord.ext import commands, tasks
from dotenv import load_dotenv
from pathlib import Path
from zoneinfo import ZoneInfo

load_dotenv(Path(__file__).parent / ".env", override=True)

from context_loader import build_system_prompt
from journal import generate_journal_entry, save_journal_entry
import reports

DISCORD_TOKEN        = os.environ["DISCORD_BOT_TOKEN"]
EVOLVED_OS_CHANNEL   = int(os.environ["EVOLVED_OS_CHANNEL_ID"])
JOURNAL_CHANNEL      = int(os.environ["JOURNAL_CHANNEL_ID"])
DAILY_REPORT_CHANNEL = int(os.environ["DAILY_REPORT_CHANNEL_ID"])
WEEKLY_REPORT_CHANNEL = int(os.environ["WEEKLY_REPORT_CHANNEL_ID"])
MAX_HISTORY          = 20

BRISBANE_TZ  = ZoneInfo("Australia/Brisbane")
REPORT_TIMES = [
    datetime.time(hour=6,  minute=0, tzinfo=BRISBANE_TZ),
    datetime.time(hour=9,  minute=0, tzinfo=BRISBANE_TZ),
    datetime.time(hour=11, minute=0, tzinfo=BRISBANE_TZ),
]

SENT_LOG = Path(__file__).parent / "sent_reports.json"
METRICS_JSON = Path(__file__).parent.parent / "context" / "current-data.json"
METRICS_REFRESH_LOCK = asyncio.Lock()

def _load_sent_log() -> dict:
    if SENT_LOG.exists():
        try:
            return json.loads(SENT_LOG.read_text())
        except Exception:
            return {}
    return {}

def _mark_sent(key: str, date_str: str):
    log = _load_sent_log()
    log[key] = date_str
    temporary = SENT_LOG.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(log, sort_keys=True))
    temporary.replace(SENT_LOG)

def _already_sent(key: str, date_str: str) -> bool:
    return _load_sent_log().get(key) == date_str

async def _refresh_metrics(*, force=False, max_age_minutes=90):
    """Refresh once, then let all report views reuse the same completed contract."""
    async with METRICS_REFRESH_LOCK:
        if not force and METRICS_JSON.exists():
            age = (
                datetime.datetime.now().timestamp()
                - METRICS_JSON.stat().st_mtime
            )
            if age <= max_age_minutes * 60:
                return True
        try:
            await asyncio.to_thread(
                subprocess.run,
                [
                    sys.executable,
                    str(
                        Path(__file__).parent.parent
                        / "scripts"
                        / "update_metrics.py"
                    ),
                ],
                check=True,
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).parent.parent),
            )
            return True
        except subprocess.CalledProcessError:
            return False  # Continue with the last completed contract.


intents                 = discord.Intents.default()
intents.message_content = True
bot                     = commands.Bot(command_prefix="/", intents=intents)
claude                  = anthropic.Anthropic()

# In-memory conversation history (resets on restart)
conversation_history: list[dict] = []

REFRESH_TRIGGERS = [
    "update-metrics", "update metrics", "refresh metrics",
    "refresh data", "update data", "pull data", "pull the data",
    "refresh kpi", "update kpi", "get latest data", "latest numbers",
]

def is_refresh_request(text: str) -> bool:
    t = text.lower()
    return any(trigger in t for trigger in REFRESH_TRIGGERS)


def trim_history():
    """Keep only the last MAX_HISTORY messages."""
    global conversation_history
    if len(conversation_history) > MAX_HISTORY * 2:
        conversation_history = conversation_history[-(MAX_HISTORY * 2):]


@tasks.loop(time=REPORT_TIMES)
async def send_daily_brief():
    today_str = datetime.date.today().isoformat()
    if _already_sent("daily", today_str):
        return
    channel = bot.get_channel(DAILY_REPORT_CHANNEL)
    if not channel:
        return
    await _refresh_metrics()
    try:
        msg = reports.format_daily_brief()
        await channel.send(msg)
        _mark_sent("daily", today_str)
    except Exception as e:
        await channel.send(f"Daily brief error: {e}")


@tasks.loop(time=REPORT_TIMES)
async def send_weekly_report():
    now = datetime.datetime.now(BRISBANE_TZ)
    if now.weekday() != 0:  # Monday only
        return
    monday_str = now.date().isoformat()
    if _already_sent("weekly", monday_str):
        return
    channel = bot.get_channel(WEEKLY_REPORT_CHANNEL)
    if not channel:
        return
    await _refresh_metrics()
    try:
        msg = reports.format_weekly_report()
        for i in range(0, len(msg), 2000):
            await channel.send(msg[i:i + 2000])
        _mark_sent("weekly", monday_str)
    except Exception as e:
        await channel.send(f"Weekly report error: {e}")


@bot.event
async def on_ready():
    print(f"Evolved OS bot online as {bot.user}")
    if not send_daily_brief.is_running():
        send_daily_brief.start()
    if not send_weekly_report.is_running():
        send_weekly_report.start()

    # Catch-up: fire any reports missed while bot was offline
    now       = datetime.datetime.now(BRISBANE_TZ)
    today_str = now.date().isoformat()
    monday_str = (now.date() - datetime.timedelta(days=now.weekday())).isoformat()

    if now.hour >= 6 and not _already_sent("daily", today_str):
        channel = bot.get_channel(DAILY_REPORT_CHANNEL)
        if channel:
            await _refresh_metrics()
            try:
                msg = reports.format_daily_brief()
                await channel.send(msg)
                _mark_sent("daily", today_str)
            except Exception as e:
                await channel.send(f"Daily brief catch-up error: {e}")

    if now.weekday() == 0 and not _already_sent("weekly", monday_str):
        channel = bot.get_channel(WEEKLY_REPORT_CHANNEL)
        if channel:
            await _refresh_metrics()
            try:
                msg = reports.format_weekly_report()
                for i in range(0, len(msg), 2000):
                    await channel.send(msg[i:i + 2000])
                _mark_sent("weekly", monday_str)
            except Exception as e:
                await channel.send(f"Weekly report catch-up error: {e}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id != EVOLVED_OS_CHANNEL:
        await bot.process_commands(message)
        return

    conversation_history.append({
        "role":    "user",
        "content": message.content,
    })
    trim_history()

    try:
        if is_refresh_request(message.content):
            await message.channel.send("Pulling fresh KPI data...")
            try:
                refreshed = await _refresh_metrics(force=True)
            except Exception as e:
                await message.channel.send(f"Refresh failed: {e}")
                return
            if not refreshed:
                await message.channel.send(
                    "Refresh failed; the last completed KPI snapshot remains active."
                )
                return

        system_prompt = build_system_prompt()

        response = claude.messages.create(
            model      = "claude-sonnet-4-6",
            max_tokens = 1024,
            system     = system_prompt,
            messages   = conversation_history,
        )

        reply = response.content[0].text

        conversation_history.append({
            "role":    "assistant",
            "content": reply,
        })
        trim_history()

        if len(reply) <= 2000:
            await message.channel.send(reply)
        else:
            for i in range(0, len(reply), 2000):
                await message.channel.send(reply[i:i + 2000])

    except Exception as e:
        await message.channel.send(f"Error: {e}")

    await bot.process_commands(message)


@bot.command(name="refresh")
async def refresh_command(ctx):
    """Pulls fresh KPI data from Google Sheets and updates current-data.md."""
    await ctx.send("Pulling fresh KPI data...")
    try:
        result = await asyncio.to_thread(
            subprocess.run,
            [sys.executable, str(Path(__file__).parent.parent / "scripts" / "update_metrics.py")],
            check=True,
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent),
        )
        # Extract the week line from output for confirmation
        week_line = next((l for l in result.stdout.splitlines() if "week" in l.lower()), "")
        await ctx.send(f"KPI data updated. {week_line}".strip())
    except subprocess.CalledProcessError as e:
        await ctx.send(f"Refresh failed: {e.stderr or e}")


@bot.command(name="journal")
async def journal_command(ctx):
    """Summarises today's #evolved-os conversation and posts to #daily-journal."""
    if ctx.channel.id != EVOLVED_OS_CHANNEL:
        await ctx.send("Use /journal in #evolved-os.")
        return

    if not conversation_history:
        await ctx.send("No conversation to summarise yet today.")
        return

    await ctx.send("Refreshing KPI data...")

    try:
        await asyncio.to_thread(
            subprocess.run,
            [sys.executable, str(Path(__file__).parent.parent / "scripts" / "update_metrics.py")],
            check=True,
            cwd=str(Path(__file__).parent.parent),
        )

        entry    = generate_journal_entry(conversation_history)
        filepath = save_journal_entry(entry)

        journal_channel = bot.get_channel(JOURNAL_CHANNEL)
        if journal_channel:
            if len(entry) <= 2000:
                await journal_channel.send(entry)
            else:
                for i in range(0, len(entry), 2000):
                    await journal_channel.send(entry[i:i + 2000])

        await ctx.send(f"Journal entry saved and posted to #daily-journal.")

    except Exception as e:
        await ctx.send(f"Journal error: {e}")


bot.run(DISCORD_TOKEN)
