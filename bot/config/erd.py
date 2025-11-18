import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent)) 

from eralchemy import render_er
from bot.config.settings import DATABASE_URL

render_er(DATABASE_URL, "erd.png")

print("ERD generated as erd.png")
