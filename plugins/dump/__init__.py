from eudplib import *

from repl.apps.repl import REPL
from repl.core.appcommand import AppCommand
from repl.encoder.const import ArgEncNumber
from repl.main import get_app_manager
from repl.main import is_bridge_mode

# initialize variables
app_manager = get_app_manager()

if not is_bridge_mode():
    raise RuntimeError("Turn on the bridge mode to use [dump] plugin")

# make commands
from .dump import DumpApp

@AppCommand([ArgEncNumber, ArgEncNumber])
def startCommand(self, ptr, size):
    '''
    Dump memory to bridge, given ptr and size
    '''
    DumpApp.setTarget(ptr, size)
    app_manager.startApplication(DumpApp)

REPL.add_command('dump', startCommand)
