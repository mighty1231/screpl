from eudplib import *

from repl import REPL, getAppManager, AppCommand, EUDByteRW, f_raiseWarning

# initialize variables
appManager = getAppManager()
superuser = appManager.superuser
v_cur_cunit, v_cur_cunitepd = EUDCreateVariables(2)
STRSection, STRSection_epd = f_dwepdread_epd(EPD(0x5993D4))

# make commands
from .manager import CUnitManagerApp

@AppCommand([])
def startCommand(self):
    appManager.startApplication(CUnitManagerApp)

REPL.addCommand('cunit', startCommand)
