from eudplib import *
from repl import (
    Application,
    AppCommand,
    argEncNumber,
    EUDByteRW
)

from . import *

def writeFirstLine(string):
    '''
    write the first line of string, excluding empty line
    '''
    reader = EUDByteRW()
    reader.seekoffset(string)

    writer = appManager.getWriter()

    writingLine = EUDVariable()
    writingLine << 0
    if EUDInfLoop()():
        b = reader.read()
        EUDBreakIf(b == 0)
        if EUDIf()([writingLine == 1, b == ord('\n')]):
            writer.write_f("...")
            EUDBreak()
        EUDEndIf()

        if EUDIfNot()(b == 0xD):
            if EUDIfNot()(b == ord('\n')):
                writingLine << 1
                writer.write(b)
            EUDEndIf()
        EUDEndIf()
    EUDEndInfLoop()

def setStringID(new_string_id):
    if EUDIf()([new_string_id >= 1, new_string_id <= string_count]):
        cur_string_id << new_string_id
    EUDEndIf()

class StringManagerApp(Application):
    def loop(self):
        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
            EUDReturn()
        if EUDElseIf()(appManager.keyPress("F7")):
            setStringID(cur_string_id - 1)
        if EUDElseIf()(appManager.keyPress("F8")):
            setStringID(cur_string_id + 1)
        if EUDElseIf()(appManager.keyPress("E", hold=["LCTRL"])):
            from .editor import StringEditorApp
            appManager.startApplication(StringEditorApp)
        if EUDElseIf()(appManager.keyPress("B", hold=["LCTRL"])):
            from .exporter import StringExporterApp
            appManager.startApplication(StringExporterApp)
        if EUDElseIf()(appManager.keyPress("F", hold=["LCTRL"])):
            from .search import StringSearchApp
            StringSearchApp.setReturn_epd(EPD(cur_string_id.getValueAddr()))
            appManager.startApplication(StringSearchApp)
        EUDEndIf()
        appManager.requestUpdate()

    def print(self, writer):
        writer.write_f("\x04StringManager id=%D / total %D strings\n", cur_string_id, string_count)
        writeFirstLine(STRSection + f_dwread_epd(STRSection_epd + cur_string_id))
        writer.write_f("\n\n\x04LCTRL+E Edit string...\n")
        writer.write_f("LCTRL+F Search strings...\n")
        writer.write_f("LCTRL+B Export to Bridge...\n")
        writer.write_f("To navigate strings, ...\n")
        writer.write_f("  - Press F7 or F8\n")
        writer.write_f("  - Use a command \"id(##)\"\n")
        writer.write(0)

    @AppCommand([argEncNumber])
    def id(self, new_string_id):
        setStringID(new_string_id)
