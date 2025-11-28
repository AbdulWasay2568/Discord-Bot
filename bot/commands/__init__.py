from .ask import ask
from .askfile import askfile
from .embed import embed
from .list import list
from .reconcile import reconcile
from .backfill import backfill

def setup_commands(bot):
    bot.add_command(ask)
    bot.add_command(askfile)
    bot.add_command(embed)
    bot.add_command(list)
    bot.add_command(reconcile)
    bot.add_command(backfill)
