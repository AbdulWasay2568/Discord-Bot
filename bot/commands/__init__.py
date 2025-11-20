from .ask import ask
from .askfile import askfile
from .embed import embed
from .list import list

def setup_commands(bot):
    bot.add_command(ask)
    bot.add_command(askfile)
    bot.add_command(embed)
    bot.add_command(list)
