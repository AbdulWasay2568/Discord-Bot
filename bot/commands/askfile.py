import discord
from discord.ext import commands
from discord import app_commands
from bot.utils.file_reader import read_file
from bot.utils.ai import generate_ai_reply

@app_commands.command(name="askfile", description="Ask a question about an uploaded file (max 5 lines)")
async def askfile(interaction: discord.Interaction, file: discord.Attachment, question: str):
    """Ask a question about the uploaded file (max 5 lines)."""
    await interaction.response.defer()
    
    file_content = await read_file(file)
    if file_content.startswith("⚠️"):
        await interaction.followup.send(file_content)
        return

    prompt = f"Here is the file content:\n{file_content}\n\nAnswer concisely in maximum 5 lines: {question}"
    reply = await generate_ai_reply(prompt)
    await interaction.followup.send(reply)
