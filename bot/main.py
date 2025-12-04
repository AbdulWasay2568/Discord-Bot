import discord
from discord.ext import commands
from bot.config.settings import DISCORD_TOKEN
from .commands import setup_commands
from bot.utils.db_handler import (
    handle_message_delete,
    handle_message_save,
    handle_message_update,
    handle_reaction_add,
    handle_reaction_remove,
)



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
    if message.author == bot.user:
        return

    await handle_message_save(message)

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
        print(f"✅ Synced {len(synced)} commands")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")
    print(f"✅ Bot is online as {bot.user}")
    print("✅ Database initialized successfully")


# ==================== RUN BOT ====================

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
