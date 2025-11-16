"""
Entry point for running the Discord bot
This file allows running the bot with: python -m bot or python bot
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.main import bot, DISCORD_TOKEN

if __name__ == "__main__":
    try:
        bot.run(DISCORD_TOKEN)
    except KeyboardInterrupt:
        print("\nBot shutting down...")
    except Exception as e:
        print(f"Error running bot: {e}")
