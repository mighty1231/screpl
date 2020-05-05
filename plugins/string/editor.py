from eudplib import *
from repl import (
    Application,
    AppTypedMethod,
    AppCommand,
    argEncNumber
)

from . import *

string_epd = EUDVariable()
cursor_epd = EUDVariable()

class StringEditorApp(Application):
    def onInit(self):
        string_epd << allocateForBuffer(cur_string_id)
        cursor_epd << string_epd

    def onDestruct(self):
        pass

    def loop(self):
        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
        EUDEndIf()
        appManager.requestUpdate()

    def print(self, writer):
        writer.write_strepd(string_epd)
        writer.write(0)
