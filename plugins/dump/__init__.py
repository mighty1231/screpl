from eudplib import *

from repl import REPL, get_app_manager, AppCommand, ArgEncNumber

# initialize variables
app_manager = get_app_manager()

if not app_manager.isBridgeMode():
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
