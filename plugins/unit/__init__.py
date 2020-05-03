from eudplib import *

from repl import REPL, getAppManager, AppCommand

# initialize variables
appManager = getAppManager()

# make commands
from .manager import UnitManagerApp

@AppCommand([])
def startCommand(self):
    appManager.startApplication(UnitManagerApp)

REPL.addCommand('unit', startCommand)
