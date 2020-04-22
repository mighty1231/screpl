from eudplib import *
from repl import (
    Application,
    AppTypedMethod,
    AppCommand,
    argEncNumber
)

from . import manager

class VariableApp(Application):
    fields = []

    def onInit(self):
        pass

    def onDestruct(self):
        pass

    def onChat(self, stringptr):
        Application.onChat(self, stringptr)

    def onResume(self):
        pass

    def loop(self):
        if EUDIf()(manager.keyPress("ESC")):
            manager.requestDestruct()
            EUDReturn()
        EUDEndIf()

    def print(self, writer):
        pass
