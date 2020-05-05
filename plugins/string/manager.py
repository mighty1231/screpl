from eudplib import *
from repl import (
    Application,
    AppTypedMethod,
    AppCommand,
    argEncNumber,
    EUDByteRW,
    Logger
)

from . import *

class StringManagerApp(Application):
    def onInit(self):
        pass

    def onChat(self, offset):
        pass

    def loop(self):
        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
        EUDEndIf()
        appManager.requestUpdate()

    def print(self, writer):
        writer.write(0)
