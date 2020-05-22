from eudplib import *

from repl.core.appcommand import AppCommand
from repl.core.application import Application
from repl.encoder.const import ArgEncNumber
from repl.utils.eudbyterw import EUDByteRW
from repl.main import is_bridge_mode

from . import *

def writeFirstLine(string):
    '''
    write the first line of string, excluding empty line
    '''
    reader = EUDByteRW()
    reader.seekoffset(string)

    writer = app_manager.getWriter()

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
        if EUDIf()(app_manager.keyPress("ESC")):
            app_manager.requestDestruct()
            EUDReturn()
        if EUDElseIf()(app_manager.keyPress("F7")):
            setStringID(cur_string_id - 1)
        if EUDElseIf()(app_manager.keyPress("F8")):
            setStringID(cur_string_id + 1)
        if EUDElseIf()(app_manager.keyPress("E", hold=["LCTRL"])):
            from .editor import StringEditorApp
            app_manager.startApplication(StringEditorApp)
        if is_bridge_mode():
            if EUDElseIf()(app_manager.keyPress("B", hold=["LCTRL"])):
                from .exporter import StringExporterApp
                app_manager.startApplication(StringExporterApp)
        if EUDElseIf()(app_manager.keyPress("F", hold=["LCTRL"])):
            from .search import StringSearchApp
            StringSearchApp.setReturn_epd(EPD(cur_string_id.getValueAddr()))
            app_manager.startApplication(StringSearchApp)
        EUDEndIf()
        app_manager.requestUpdate()

    def print(self, writer):
        writer.write_f("\x04StringManager id=%D / total %D strings\n", cur_string_id, string_count)
        writeFirstLine(STRSection + f_dwread_epd(STRSection_epd + cur_string_id))
        writer.write_f("\n\n\x04LCTRL+E Edit string...\n")
        writer.write_f("LCTRL+F Search strings...\n")
        if is_bridge_mode():
            writer.write_f("LCTRL+B Export to Bridge...\n")
        writer.write_f("To navigate strings, ...\n")
        writer.write_f("  - Press F7 or F8\n")
        writer.write_f("  - Use a command \"id(##)\"\n")
        writer.write(0)

    @AppCommand([ArgEncNumber])
    def id(self, new_string_id):
        setStringID(new_string_id)
