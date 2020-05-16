from eudplib import *

from repl import REPL, getAppManager, AppCommand, argEncNumber

# initialize variables
appManager = getAppManager()

if not appManager.isBridgeMode():
    raise RuntimeError("Turn on the bridge mode to use [dump] plugin")

# make commands
from .dump import DumpApp

@AppCommand([argEncNumber, argEncNumber])
def startCommand(self, ptr, size):
    '''
    Dump memory to bridge, given ptr and size
    '''
    DumpApp.setTarget(ptr, size)
    appManager.startApplication(DumpApp)

REPL.addCommand('dump', startCommand)
