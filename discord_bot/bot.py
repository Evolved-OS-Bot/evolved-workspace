#!/usr/bin/env python3
"""
bot.py
Evolved OS Discord bot.
- #evolved-os: direct Claude chat with full workspace context
- /journal: summarises the day's conversation and posts to #daily-journal
"""

import os
import subprocess
import sys
import discord
import anthropic
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env", override=True)

from context_loader import build_system_prompt
from journal import generate_journal_entry, save_journal_entry

DISCORD_TOKEN      = os.environ["DISCORD_BOT_TOKEN"]
EVOLVED_OS_CHANNEL = int(os.environ["EVOLVED_OS_CHANNEL_ID"])
JOURNAL_CHANNEL    = int(os.environ["JOURNAL_CHANNEL_ID"])
MAX_HISTORY        = 20

intents                 = discord.Intents.default()
intents.message_content = True
bot                     = commands.Bot(command_prefix="/", intents=intents)
claude                  = anthropic.Anthropic()

# In-memory conversation history (resets on restart)
conversation_history: list[dict] = []


def trim_history():
    """Keep only the last MAX_HISTORY messages."""
    global conversation_history
    if len(conversation_history) > MAX_HISTORY * 2:
        conversation_history = conversation_history[-(MAX_HISTORY * 2):]


@bot.event
async def on_ready():
    print(f"Evolved OS bot online as {bot.user}")


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
        subprocess.run(
            [sys.executable, str(Path(__file__).parent.parent / "scripts" / "update_metrics.py")],
            check=True,
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
