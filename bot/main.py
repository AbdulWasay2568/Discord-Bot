import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from bot.utils.ai import generate_ai_reply
from bot.utils.db_handler import handle_message_save, handle_reaction_add, handle_reaction_remove
from bot.commands import ask, askfile, backup  # import commands
from db.db_utils import create_db

# ---------------- ENV ----------------
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Initialize database
create_db()

# ---------------- Discord Setup ----------------
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Register commands
bot.add_command(ask.ask)
bot.add_command(askfile.askfile)
bot.add_command(backup.backup)
bot.add_command(backup.backup_stats)

# ==================== MESSAGE EVENTS ====================
@bot.event
async def on_message(message: discord.Message):
    # Save message to database
    if not message.author.bot:
        await handle_message_save(message)
    
    if message.author == bot.user:
        return

    await bot.process_commands(message)

    # AI reply when mentioned
    if bot.user.mentioned_in(message):
        prompt = message.clean_content.replace(f"@{bot.user.name}", "").strip()
        if not prompt:
            return
        async with message.channel.typing():
            concise_prompt = f"Answer concisely in maximum 5 lines: {prompt}"
            reply = await generate_ai_reply(concise_prompt)
            await message.reply(reply)

# ==================== REACTION EVENTS ====================
@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    """Save reaction when added"""
    await handle_reaction_add(reaction, user)

@bot.event
async def on_reaction_remove(reaction: discord.Reaction, user: discord.User):
    """Remove reaction from database"""
    await handle_reaction_remove(reaction, user)

# ==================== BOT READY ====================
@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    print(f"Database initialized successfully")

# ==================== RUN BOT ====================
bot.run(DISCORD_TOKEN)
