import discord
from discord import app_commands
from bot.utils.db_handler import reconcile_channel

@app_commands.command(name="reconcile", description="Reconcile the current channel with Discord history")
async def reconcile(interaction: discord.Interaction):
    try:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("Bot is working on this...", ephemeral=True)
        await reconcile_channel(interaction.channel, backfill=False)
        await interaction.followup.send("Channel reconciled completely.", ephemeral=True)
    except Exception as e:
        print(f"Error reconciling channel {interaction.channel.id}: {e}")
        await interaction.followup.send(f"Error: {str(e)}", ephemeral=True)