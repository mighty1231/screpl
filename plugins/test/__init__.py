from repl import REPL, getAppManager, AppCommand

manager = getAppManager()

@AppCommand([])
def startCommand(self):
    getAppManager().startApplication(TestApp)

@AppCommand([])
def startCommand2(self):
    getAppManager().startApplication(TestApp2)

from .app import TestApp
from .scrolltest import TestApp2

REPL.addCommand('test', startCommand)
REPL.addCommand('test2', startCommand2)
