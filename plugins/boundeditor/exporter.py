'''
TUI
 1. Bound Editor - Exporter (Bridge Client required)
 2. Death Variable Unit - {Cave}
 3. turbo mode - eudturbo, turbo, nothing
 4.
 5. Press CTRL+Y to EXPORT
 6.
 7.
 8.
 9.
10.
11.
'''


from eudplib import *
from repl import (
    Application,
    AppTypedMethod,
    AppCommand,
    argEncNumber
)

from . import appManager

TURBO_EUD = 0
TURBO_NORMAL = 1
TURBO_NOTHING = 2
turbo_mode = EUDVariable()


class ExporterApp(Application):
    def onInit(self):
        pass

    def onDestruct(self):
        pass

    def loop(self):
        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
        if EUDElseIf()(appManager.keyPress("K")):
            appManager.exportAppOutputToBridge(Db("ABCD"), 4)
        EUDEndIf()
        appManager.requestUpdate()

    def print(self, writer):
        writer.write(0)
