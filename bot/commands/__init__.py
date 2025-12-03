from .ask import ask
from .askfile import askfile
from .embed import embed
from .list import list
from .reconcile import reconcile
from .backfill import backfill

def setup_commands(bot):
    # Register slash commands
    bot.tree.add_command(ask)
    bot.tree.add_command(askfile)
    bot.tree.add_command(embed)
    bot.tree.add_command(list)
    bot.tree.add_command(reconcile)
    bot.tree.add_command(backfill)
