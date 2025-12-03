import discord
from discord import app_commands
from bot.utils.ai import generate_ai_reply


@app_commands.command(name="ask", description="Ask a concise question to Gemini AI (max 5 lines)")
async def ask(interaction: discord.Interaction, prompt: str):
    concise_prompt = f"Answer concisely in maximum 5 lines: {prompt}"
    await interaction.response.defer(ephemeral=True)
    reply = await generate_ai_reply(concise_prompt)
    await interaction.followup.send(reply, ephemeral=True)
