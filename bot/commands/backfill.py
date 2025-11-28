from discord.ext import commands
from bot.utils.db_handler import reconcile_channel

@commands.command()
async def backfill(ctx):
    try:
        await reconcile_channel(ctx.channel, backfill=True)
        await ctx.reply("Channel backfilled successfully.")
    except Exception as e:
        print(f"Error backfilling channel {ctx.channel.id}: {e}")