from eudplib import *
from repl import (
    Application,
    AppTypedMethod,
    AppCommand,
    argEncNumber
)

from . import appManager

_cunit_epd = EUDVariable()

def f_epd2ptr(epd):
    return 0x58A364 + (epd * 4)

class CUnitDetailApp(Application):
    fields = [
        "cunit_epd",
        "offset"
    ]
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
        writer.write_f("\x04CUnit Detail (ptr=%H)\n", f_epd2ptr(self.cunit_epd))

        writer.write(0)
