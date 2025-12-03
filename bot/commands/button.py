import discord
from discord import app_commands
import os

AUTHOR = os.getenv("AUTHOR")

class myView(discord.ui.View):
    @discord.ui.button(label="Click")
    async def click(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
           await interaction.response.send_message("Button is clicked", ephemeral=False)
        except Exception as e:
            print(e)

@app_commands.command(name="button", description="Send a message with a button")
async def button(interaction: discord.Interaction):
    view = myView()
    await interaction.response.send_message("this is button", view=view)
