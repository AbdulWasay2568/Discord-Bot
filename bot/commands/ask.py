from discord.ext import commands
from bot.utils.ai import generate_ai_reply


@commands.command()
async def ask(ctx, *, prompt: str):
    """Ask a concise question to Gemini AI (max 5 lines)."""
    concise_prompt = f"Answer concisely in maximum 5 lines: {prompt}"
    async with ctx.typing():
        reply = await generate_ai_reply(concise_prompt)
    await ctx.reply(reply)

