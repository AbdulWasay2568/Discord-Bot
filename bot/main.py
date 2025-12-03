import discord
from discord.ext import commands
from discord import app_commands
from bot.config.settings import DISCORD_TOKEN
from .commands import setup_commands
from bot.utils.db_handler import (
    handle_message_delete,
    handle_message_save,
    handle_message_update,
    handle_reaction_add,
    handle_reaction_remove,
)

from bot.utils.ai import generate_ai_reply



# ==================== INITIAL SETUP ====================

# Discord Intent Settings
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guild_messages = True
intents.reactions = True
intents.guilds = True
intents.members = True      
intents.guild_reactions = True   

# Bot instance (slash commands don't use command_prefix)
bot = commands.Bot(command_prefix=None, intents=intents)


# ==================== LOAD COMMANDS ====================

setup_commands(bot)


# ==================== MESSAGE EVENTS ====================

@bot.event
async def on_message(message: discord.Message):    
    # Save all incoming messages (bot + user)
    await handle_message_save(message)

    # Avoid bot self-triggering
    if message.author == bot.user:
        return

    # AI reply when mentioned
    if bot.user.mentioned_in(message):
        prompt = message.clean_content.replace(f"@{bot.user.name}", "").strip()

        if not prompt:
            return

        async with message.channel.typing():
            concise_prompt = f"Answer concisely in maximum 5 lines: {prompt}"
            reply = await generate_ai_reply(concise_prompt)
            await message.reply(reply)

@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    await handle_message_update(after)


@bot.event
async def on_message_delete(message: discord.Message):
    await handle_message_delete(message)

# ==================== REACTION EVENTS ====================

@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    await handle_reaction_add(reaction, user)

@bot.event
async def on_reaction_remove(reaction: discord.Reaction, user: discord.User):
    await handle_reaction_remove(reaction, user)

# ==================== BOT READY ====================

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")
    
    print(f"✅ Bot is online as {bot.user}")
    print("✅ Database initialized successfully")


# ==================== RUN BOT ====================

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
