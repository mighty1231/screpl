from eudplib import *
from repl import (
    Application,
    AppTypedMethod,
    AppCommand,
    argEncNumber
)

from . import *

class CUnitOptionApp(Application):
    def onInit(self):
        pass

    def onDestruct(self):
        pass

    def loop(self):
        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
            EUDReturn()
        EUDEndIf()
        appManager.requestUpdate()

    def print(self, writer):
        writer.write_f("\x04Choose which member you will observe\n")
        writer.write(0)
