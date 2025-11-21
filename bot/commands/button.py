import sys
from pathlib import Path
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
load_dotenv()
AUTHOR = os.getenv("AUTHOR")

class myView(discord.ui.View):
    @discord.ui.button(label="Click")
    async def click(self,interaction:discord.Interaction, button: discord.ui.Button):
        try:
           await interaction.response.send_message("Button is clicked", ephemeral=False)
        except Exception as e:
            print(e)

# class myView(discord.ui.View):
#     @discord.ui.button(label="Click")
#     async def click(self, interaction: discord.Interaction, button: discord.ui.Button):
#         await interaction.response.send_message("Button is clicked", ephemeral=True)



@commands.command()
async def button(ctx):
    view = myView()
    await ctx.reply("this is button",view=view)
