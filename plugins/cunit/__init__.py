from eudplib import *

from repl import REPL, getAppManager, AppCommand, EUDByteRW, f_raiseWarning

# initialize variables
appManager = getAppManager()
superuser = appManager.superuser
v_cur_cunit, v_cur_cunitepd = EUDCreateVariables(2)

# members
from .cunitrw import cu_members
for entry in cu_members:


# make commands
from .manager import CUnitManagerApp

@AppCommand([])
def startCommand(self):
    appManager.startApplication(CUnitManagerApp)

REPL.addCommand('cunit', startCommand)
