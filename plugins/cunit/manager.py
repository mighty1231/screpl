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
    def onInit(self):
        pass

    def onDestruct(self):
        pass

    def loop(self):
        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
            EUDReturn()
        if EUDElseIf()(appManager.keyPress("H", hold=["LCTRL"])):
            dw, epd = f_dwepdcunitread_epd(EPD(0x6284B8))
            v_cur_cunit << dw
            v_cur_cunitepd << epd
        if EUDElseIf()(appManager.keyPress("E", hold=["LCTRL"])):
            appManager.startApplication(CUnitDetailApp)
        if EUDElseIf()(appManager.keyPress("O", hold=["LCTRL"])):
            appManager.startApplication(CUnitOptionApp)
        EUDEndIf()
        appManager.requestUpdate()

    def print(self, writer):
        writer.write_f("\x04CUnit Manager (Current ptr=%H)\n", v_cur_cunit)
        writer.write_f("LCTRL+H Set CUnit pointer as selected\n")
        if EUDIfNot()(v_cur_cunit == 0):
            writer.write_f("LCTRL+E Open CUnitDetailApp\n")
        EUDEndIf()
        writer.write_f("LCTRL+O Options\n")
        writer.write(0)
