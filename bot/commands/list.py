from discord.ext import commands
import discord

@commands.command()
async def list(ctx):
    await ctx.send("This is lsit command")
