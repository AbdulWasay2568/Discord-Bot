import io
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import openpyxl
import discord

MAX_FILE_SIZE_MB = 5
MAX_FILE_CONTENT = 4000  

async def read_file(file: discord.Attachment) -> str:
    """Read file content with size/content checks."""
    if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        return f"⚠️ File size exceeds {MAX_FILE_SIZE_MB} MB limit."

    try:
        file_bytes = await file.read()
        content = ""
        filename = file.filename.lower()

        if filename.endswith((".txt", ".csv")):
            content = file_bytes.decode('utf-8', errors='ignore')

        elif filename.endswith(".pdf"):
            pdf_reader = PdfReader(io.BytesIO(file_bytes))
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    content += page_text + "\n"

        elif filename.endswith((".png", ".jpg", ".jpeg", ".bmp")):
            try:
                image = Image.open(io.BytesIO(file_bytes))
                content = pytesseract.image_to_string(image)
                if not content.strip():
                    content = "⚠️ No text detected in the image."
            except Exception:
                return "⚠️ Cannot process image (is Tesseract installed?)."

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

        else:
            content = file_bytes.decode('utf-8', errors='ignore')

        return content[:MAX_FILE_CONTENT]

    except Exception as e:
        return f"⚠️ Error reading file: {str(e)}"
