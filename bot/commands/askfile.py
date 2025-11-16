import sys
from pathlib import Path
from discord.ext import commands

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from bot.utils.file_reader import read_file
from bot.utils.ai import generate_ai_reply

@commands.command()
async def askfile(ctx, *, command: str):
    """Ask a question about the uploaded file (max 5 lines)."""
    if not ctx.message.attachments:
        await ctx.reply("⚠️ Please attach a file to use this command.")
        return

    file = ctx.message.attachments[0]

    async with ctx.typing():
        file_content = await read_file(file)
        if file_content.startswith("⚠️"):
            await ctx.reply(file_content)
            return

        prompt = f"Here is the file content:\n{file_content}\n\nAnswer concisely in maximum 5 lines: {command}"
        reply = await generate_ai_reply(prompt)
        await ctx.reply(reply)
