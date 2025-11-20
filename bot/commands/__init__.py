from .ask import ask
from .askfile import askfile


def setup_commands(bot):
    """Register all commands in a clean way."""
    bot.add_command(ask)
    bot.add_command(askfile)
