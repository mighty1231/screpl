'''
focused cunit
cunit viewer
option - what to view
'''
from eudplib import *
from repl import (
    Application,
    AppTypedMethod,
    AppCommand,
    argEncNumber
)

from . import *
from .detail import CUnitDetailApp
from .option import CUnitOptionApp

class CUnitManagerApp(Application):
    def loop(self):
        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
            EUDReturn()
        if EUDElseIf()(appManager.keyPress("E", hold=["LCTRL"])):
            appManager.startApplication(CUnitDetailApp)
        if EUDElseIf()(appManager.keyPress("O", hold=["LCTRL"])):
            appManager.startApplication(CUnitOptionApp)
        EUDEndIf()
        appManager.requestUpdate()

    def print(self, writer):
        writer.write_f("\x04CUnit Manager\n")
        writer.write_f("LCTRL+E Open CUnitDetailApp\n")
        writer.write_f("LCTRL+O Options\n")
        writer.write(0)
