from repl import REPL, getAppManager, AppCommand

appManager = getAppManager()

from .app import TestApp
from .scrolltest import TestApp2
from .arraytest import ArrayTestApp
from .recursivetest import RecursiveTestApp

@AppCommand([])
def startCommand(self):
    appManager.startApplication(TestApp)

@AppCommand([])
def startCommand2(self):
    appManager.startApplication(TestApp2)

@AppCommand([])
def startCommand3(self):
    appManager.startApplication(ArrayTestApp)

REPL.addCommand('test', startCommand)
REPL.addCommand('test2', startCommand2)
REPL.addCommand('arraytest', startCommand3)
