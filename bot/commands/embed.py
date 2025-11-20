from discord.ext import commands
import discord

@commands.command()
async def embed(ctx):
    embed = discord.Embed(
        title="Hello!",
        description="This is an embed example.",
        color=discord.Color.blue()
    )
    embed.add_field(name="Field 1", value="Value 1", inline=False)
    embed.set_footer(text="Footer text")
    embed.set_thumbnail(url="https://example.com/image.png")

    await ctx.send(embed=embed)
