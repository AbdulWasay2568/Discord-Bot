from discord.ext import commands
from bot.utils.db_handler import reconcile_channel

@commands.command()
async def reconcile(ctx):
    try:
        await reconcile_channel(ctx.channel, backfill=False)
        await ctx.send("Channel reconciled successfully.")
    except Exception as e:
        print(f"Error reconciling channel {ctx.channel.id}: {e}")