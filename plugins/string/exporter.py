from eudplib import *
from repl import (
    Application,
    AppTypedMethod,
    AppCommand,
    argEncNumber
)

from . import *

class StringExporterApp(Application):
    def onInit(self):
        pass

    def onDestruct(self):
        pass

    def loop(self):
        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
        EUDEndIf()
        appManager.requestUpdate()

    def print(self, writer):
        writer.write(0)
