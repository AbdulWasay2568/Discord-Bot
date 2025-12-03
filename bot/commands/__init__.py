from .ask import ask
from .askfile import askfile
from .list import list
from .reconcile import reconcile
from .backfill import backfill

def setup_commands(bot):
    bot.tree.add_command(ask)
    bot.tree.add_command(askfile)
    bot.tree.add_command(list)
    bot.tree.add_command(reconcile)
    bot.tree.add_command(backfill)
