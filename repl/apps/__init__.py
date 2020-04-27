from ..core import AppCommand, getAppManager
from .static import StaticApp
from .scroll import ScrollApp
from .logger import Logger
from .iocheck import IOCheck
from .repl import REPL

@AppCommand([])
def _help(self):
    StaticApp.setContent(
        'SC-REPL manual',
        '\x13SC-REPL\n'
        + '\x13Made by sixthMeat (mighty1231@gmail.com)\n'
        + '\n'
        + 'Key Inputs\n'
        + '- F7: Search previous page\n'
        + '- F8: Search next page\n'
        + '\n'
        + 'builtin functions\n'
        + 'help() - See manual\n'
        + 'cmds() - See registered commands\n'
    )
    getAppManager().startApplication(StaticApp)

@AppCommand([])
def _log(self):
    getAppManager().startApplication(Logger)

REPL.addCommand("help", _help)
REPL.addCommand("log", _log)
