from eudplib import *
from eudplib.core.mapdata.stringmap import locmap

from repl import REPL, getAppManager, AppCommand, EPDConstString

# initialize variables
manager = getAppManager()

def getUsedDeathUnits():
    trig = GetChkTokenized().getsection(b'TRIG')

# make commands
from .varapp import VariableApp

@AppCommand([])
def startCommand(self):
    manager.startApplication(VariableApp)

REPL.addCommand('variable', startCommand)
