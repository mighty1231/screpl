from eudplib import *

from screpl.apps.repl import REPL
from screpl.core.appcommand import AppCommand
from screpl.encoder.const import ArgEncNumber
from screpl.main import get_app_manager
from screpl.main import is_bridge_mode

# initialize variables
app_manager = get_app_manager()

if not is_bridge_mode():
    raise RuntimeError("Turn on the bridge mode to use 'dump' plugin")

def plugin_setup():
    # make commands
    from .dump import DumpApp

    @AppCommand([ArgEncNumber, ArgEncNumber])
    def startCommand(self, ptr, size):
        '''
        Dump memory to bridge, given ptr and size
        '''
        DumpApp.setTarget(ptr, size)
        app_manager.start_application(DumpApp)

    REPL.add_command('dump', startCommand)
