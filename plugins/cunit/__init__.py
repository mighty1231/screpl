from eudplib import *

from repl import REPL, getAppManager, AppCommand, Array

# initialize variables
appManager = getAppManager()
superuser = appManager.superuser

# members
from .cunitrw import cu_members
cu_mem_activeids = Array.construct(cu_members.length, list(range(cu_members.length)))
cu_mem_activeid_contents = cu_mem_activeids.contents

# make commands
from .manager import CUnitManagerApp

@AppCommand([])
def startCommand(self):
    appManager.startApplication(CUnitManagerApp)

REPL.addCommand('cunit', startCommand)
