import os
import sys
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.utils.ai import generate_ai_reply
from bot.utils.db_handler import handle_message_save, handle_reaction_add, handle_reaction_remove
from bot.commands.ask import ask
from bot.commands.askfile import askfile
from bot.commands.backup import backup, backup_stats
from db.db_utils import create_db

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

create_db()

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix="!", intents=intents)

bot.add_command(ask)
bot.add_command(askfile)
bot.add_command(backup)
bot.add_command(backup_stats)

@bot.event
async def on_message(message: discord.Message):
    await handle_message_save(message)
    
    if message.author == bot.user:
        return

    await bot.process_commands(message)

    if bot.user.mentioned_in(message):
        prompt = message.clean_content.replace(f"@{bot.user.name}", "").strip()
        if not prompt:
            return
        async with message.channel.typing():
            concise_prompt = f"Answer concisely in maximum 5 lines: {prompt}"
            reply = await generate_ai_reply(concise_prompt)
            await message.reply(reply)


@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    """Save reaction when added"""
    await handle_reaction_add(reaction, user)

@bot.event
async def on_reaction_remove(reaction: discord.Reaction, user: discord.User):
    """Remove reaction from database"""
    await handle_reaction_remove(reaction, user)


@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    print(f"Database initialized successfully")

bot.run(DISCORD_TOKEN)
