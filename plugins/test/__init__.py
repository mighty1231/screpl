from repl import REPL, getAppManager, AppCommand

appManager = getAppManager()

from .app import TestApp
from .scrolltest import TestApp2
from .arraytest import ArrayTestApp

@AppCommand([])
def startCommand(self):
    getAppManager().startApplication(TestApp)

@AppCommand([])
def startCommand2(self):
    getAppManager().startApplication(TestApp2)

@AppCommand([])
def startCommand3(self):
    getAppManager().startApplication(ArrayTestApp)


REPL.addCommand('test', startCommand)
REPL.addCommand('test2', startCommand2)
REPL.addCommand('arraytest', startCommand3)
