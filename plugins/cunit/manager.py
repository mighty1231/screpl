'''
focused cunit
cunit viewer
option - what to view
'''
from eudplib import *

from screpl.core.appcommand import AppCommand
from screpl.core.application import Application
from screpl.encoder.const import ArgEncNumber

from . import *
from .detail import CUnitDetailApp
from .option import CUnitOptionApp

class CUnitManagerApp(Application):
    def loop(self):
        if EUDIf()(app_manager.key_press("ESC")):
            app_manager.request_destruct()
            EUDReturn()
        if EUDElseIf()(app_manager.key_press("E", hold=["LCTRL"])):
            app_manager.start_application(CUnitDetailApp)
        if EUDElseIf()(app_manager.key_press("O", hold=["LCTRL"])):
            app_manager.start_application(CUnitOptionApp)
        EUDEndIf()
        app_manager.request_update()

    def print(self, writer):
        writer.write_f("\x04CUnit Manager\n")
        writer.write_f("LCTRL+E Open CUnitDetailApp\n")
        writer.write_f("LCTRL+O Options\n")
        writer.write(0)
