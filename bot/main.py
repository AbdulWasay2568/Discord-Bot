import discord
from discord.ext import commands
from bot.config.settings import DISCORD_TOKEN
from db.db_utils import create_db
from bot.commands import setup_commands
from bot.utils.db_handler import (
    handle_message_save,
    handle_reaction_add,
    handle_reaction_remove,
)

from bot.utils.ai import generate_ai_reply



# ==================== INITIAL SETUP ====================

# Initialize database
create_db()

# Discord Intent Settings
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

# Bot instance
bot = commands.Bot(command_prefix="!", intents=intents)


# ==================== LOAD COMMANDS ====================

setup_commands(bot)


# ==================== MESSAGE EVENTS ====================

@bot.event
async def on_message(message: discord.Message):
    """Handle incoming messages"""
    
    # Save all incoming messages (bot + user)
    await handle_message_save(message)

    # Avoid bot self-triggering
    if message.author == bot.user:
        return

    # Allow commands to work
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
    print(f"✅ Bot is online as {bot.user}")
    print("✅ Database initialized successfully")


# ==================== RUN BOT ====================

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
