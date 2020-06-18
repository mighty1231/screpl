"""Defines CUnitManagerApp

TUI

.. code-block:: text

    CUnit Manager
    LCTRL+E Open CUnitDetailApp
    LCTRL+O Options
    LCTRL+G ReadStruct
"""
from eudplib import *

from screpl.core.application import Application
from screpl.main import is_bridge_mode

from . import app_manager
from .detail import CUnitDetailApp
from .option import CUnitOptionApp
from .readstruct import ReadStructApp

class CUnitManagerApp(Application):
    def loop(self):
        if EUDIf()(app_manager.key_press("ESC")):
            app_manager.request_destruct()
        if EUDElseIf()(app_manager.key_press("E", hold=["LCTRL"])):
            app_manager.start_application(CUnitDetailApp)
        if EUDElseIf()(app_manager.key_press("O", hold=["LCTRL"])):
            app_manager.start_application(CUnitOptionApp)
        if is_bridge_mode():
            if EUDElseIf()(app_manager.key_press("G", hold=["LCTRL"])):
                app_manager.start_application(ReadStructApp)
        EUDEndIf()
        app_manager.request_update()

    def print(self, writer):
        writer.write_f("\x04CUnit Manager\n")
        writer.write_f("LCTRL+E Open CUnitDetailApp\n")
        writer.write_f("LCTRL+O Options\n")
        if is_bridge_mode():
            writer.write_f("LCTRL+G ReadStruct\n")
        writer.write(0)
