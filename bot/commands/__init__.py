from .ask import ask
from .askfile import askfile
from .backup import backup, backup_stats


def setup_commands(bot):
    """Register all commands in a clean way."""
    bot.add_command(ask)
    bot.add_command(askfile)
    bot.add_command(backup)
    bot.add_command(backup_stats)
