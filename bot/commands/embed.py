import discord
from discord.ext import commands
from discord import app_commands

@app_commands.command(name="embed", description="Send an example embed")
async def embed(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Hello!",
        description="This is an embed example.",
        color=discord.Color.blue()
    )
    embed.add_field(name="Field 1", value="Value 1", inline=False)
    embed.set_footer(text="Footer text")
    embed.set_thumbnail(url="https://example.com/image.png")

    await interaction.response.send_message(embed=embed)
