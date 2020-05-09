from ..core import AppCommand, getAppManager
from ..resources.encoder.const import argEncNumber
from .static import StaticApp
from .scroll import ScrollApp
from .logger import Logger
from .iocheck import IOCheck
from .repl import REPL
from .chatreader import ChatReaderApp
from .selector import (
    AIScriptSelectorApp,
    ModifierSelectorApp,
    AllyStatusSelectorApp,
    ComparisonSelectorApp,
    OrderSelectorApp,
    PlayerSelectorApp,
    PropStateSelectorApp,
    ResourceSelectorApp,
    ScoreSelectorApp,
    SwitchActionSelectorApp,
    SwitchStateSelectorApp
)

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
        + 'cmds() - See registered commands'
    )
    getAppManager().startApplication(StaticApp)

@AppCommand([])
def _log(self):
    getAppManager().startApplication(Logger)

@AppCommand([argEncNumber])
def _setTriggerDelay(self, delay):
    getAppManager().setTriggerDelay(delay)
    writer = getAppManager().getWriter()
    writer.seekepd(self.cmd_output_epd)
    writer.write_f("Now trigger delay is %D (0:eudturbo, 1:turbo)", delay)
    writer.write(0)

@AppCommand([])
def _unsetTriggerDelay(self):
    getAppManager().unsetTriggerDelay()
    writer = getAppManager().getWriter()
    writer.seekepd(self.cmd_output_epd)
    writer.write_f("Unset trigger delay")
    writer.write(0)

REPL.addCommand("help", _help)
REPL.addCommand("log", _log)
REPL.addCommand("delay", _setTriggerDelay)
REPL.addCommand("delayOFF", _unsetTriggerDelay)
