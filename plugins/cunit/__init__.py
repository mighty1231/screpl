from eudplib import *

from repl.apps.repl import REPL
from repl.core.appcommand import AppCommand
from repl.main import get_app_manager
from repl.utils.array import REPLArray

# initialize variables
app_manager = get_app_manager()

# members
from .cunitrw import cu_members
cu_mem_activeids = REPLArray.construct(cu_members.length, list(range(cu_members.length)))
cu_mem_activeid_contents = cu_mem_activeids.contents

# make commands
from .manager import CUnitManagerApp

@AppCommand([])
def startCommand(self):
    app_manager.startApplication(CUnitManagerApp)

REPL.add_command('cunit', startCommand)
