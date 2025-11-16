import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-flash-latest")

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
