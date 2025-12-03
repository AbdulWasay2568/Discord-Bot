import discord
from discord.ext import commands
from discord import app_commands
from bot.utils.db_handler import reconcile_channel

@app_commands.command(name="backfill", description="Backfill the current channel with older Discord messages")
async def backfill(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        await interaction.followup.send("Bot is working on this...", ephemeral=True)
        await reconcile_channel(interaction.channel, backfill=True)
        await interaction.followup.send("Channel backfilled completely.", ephemeral=True)
    except Exception as e:
        print(f"Error backfilling channel {interaction.channel.id}: {e}")
        await interaction.followup.send(f"Error: {str(e)}")
