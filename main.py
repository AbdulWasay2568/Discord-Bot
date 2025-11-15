import os
import io
import discord
from discord.ext import commands
from dotenv import load_dotenv
import google.generativeai as genai

# For PDFs
from PyPDF2 import PdfReader

# For images OCR
from PIL import Image
import pytesseract

# For Excel
import openpyxl

# ---------------- ENV ----------------
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

# ---------------- Gemini Setup ----------------
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-flash-latest")

# ---------------- Discord Setup ----------------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- AI FUNCTION ----------------
async def generate_ai_reply(prompt: str) -> str:
    """
    Generate a concise answer from Gemini AI (max 5 lines).
    """
    try:
        response = model.generate_content(prompt)
        lines = response.text.strip().splitlines()
        return "\n".join(lines[:5])
    except Exception as e:
        return f"⚠️ Gemini Error: {str(e)}"

# ---------------- FILE READING ----------------
MAX_FILE_SIZE_MB = 5
MAX_FILE_CONTENT = 4000  # characters

async def read_file(file: discord.Attachment) -> str:
    """
    Read file content with size/content checks.
    Supports txt, csv, pdf, image (OCR), and Excel (.xlsx).
    """
    if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        return f"⚠️ File size exceeds {MAX_FILE_SIZE_MB} MB limit."

    try:
        file_bytes = await file.read()
        content = ""
        filename = file.filename.lower()

        # Text / CSV files
        if filename.endswith((".txt", ".csv")):
            content = file_bytes.decode('utf-8', errors='ignore')

        # PDF files
        elif filename.endswith(".pdf"):
            pdf_reader = PdfReader(io.BytesIO(file_bytes))
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    content += page_text + "\n"

        # Image files (OCR)
        elif filename.endswith((".png", ".jpg", ".jpeg", ".bmp")):
            try:
                image = Image.open(io.BytesIO(file_bytes))
                content = pytesseract.image_to_string(image)
                if not content.strip():
                    content = "⚠️ No text detected in the image."
            except Exception:
                return "⚠️ Cannot process image (is Tesseract installed?)."

        # Excel files (.xlsx)
        elif filename.endswith(".xlsx"):
            try:
                wb = openpyxl.load_workbook(filename=io.BytesIO(file_bytes), data_only=True)
                sheet = wb.active
                rows = []
                for row in sheet.iter_rows(values_only=True):
                    rows.append([str(cell) if cell is not None else "" for cell in row])
                content = "\n".join([", ".join(r) for r in rows])
            except Exception as e:
                return f"⚠️ Error reading Excel file: {str(e)}"

        # Other files: attempt decoding as text
        else:
            content = file_bytes.decode('utf-8', errors='ignore')

        return content[:MAX_FILE_CONTENT]

    except Exception as e:
        return f"⚠️ Error reading file: {str(e)}"

# ---------------- COMMANDS -------------------
@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

# Ask a direct question (text)
@bot.command()
async def ask(ctx, *, prompt: str):
    concise_prompt = f"Answer concisely in maximum 5 lines: {prompt}"
    async with ctx.typing():
        reply = await generate_ai_reply(concise_prompt)
    await ctx.reply(reply)

# Ask a question about a file
@bot.command()
async def askfile(ctx, *, command: str):
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

# ---------------- Chat without commands ----------------
@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

    if bot.user.mentioned_in(message):
        prompt = message.clean_content.replace(f"@{bot.user.name}", "").strip()
        if not prompt:
            return
        async with message.channel.typing():
            concise_prompt = f"Answer concisely in maximum 5 lines: {prompt}"
            reply = await generate_ai_reply(concise_prompt)
            await message.reply(reply)

# ---------------- RUN BOT ----------------
bot.run(DISCORD_TOKEN)
