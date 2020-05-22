from eudplib import *

from repl import REPL, get_app_manager, AppCommand, REPLArray

# initialize variables
app_manager = get_app_manager()
superuser = app_manager.superuser

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
