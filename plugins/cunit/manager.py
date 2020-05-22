'''
focused cunit
cunit viewer
option - what to view
'''
from eudplib import *

from repl.core.appcommand import AppCommand
from repl.core.application import Application
from repl.encoder.const import ArgEncNumber

from . import *
from .detail import CUnitDetailApp
from .option import CUnitOptionApp

class CUnitManagerApp(Application):
    def loop(self):
        if EUDIf()(app_manager.keyPress("ESC")):
            app_manager.requestDestruct()
            EUDReturn()
        if EUDElseIf()(app_manager.keyPress("E", hold=["LCTRL"])):
            app_manager.startApplication(CUnitDetailApp)
        if EUDElseIf()(app_manager.keyPress("O", hold=["LCTRL"])):
            app_manager.startApplication(CUnitOptionApp)
        EUDEndIf()
        app_manager.requestUpdate()

    def print(self, writer):
        writer.write_f("\x04CUnit Manager\n")
        writer.write_f("LCTRL+E Open CUnitDetailApp\n")
        writer.write_f("LCTRL+O Options\n")
        writer.write(0)
