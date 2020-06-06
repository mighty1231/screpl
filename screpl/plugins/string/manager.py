from eudplib import *

from screpl.core.appcommand import AppCommand
from screpl.core.application import Application
from screpl.encoder.const import ArgEncNumber
from screpl.utils.byterw import REPLByteRW
from screpl.main import is_bridge_mode, get_main_writer

from . import *

v_result_epd = EUDVariable(EPD(0))

def _write_first_line(string):
    '''
    write the first line of string, excluding empty line
    '''
    reader = REPLByteRW()
    reader.seekoffset(string)

    writer = get_main_writer()

    writing_line = EUDVariable()
    writing_line << 0
    if EUDInfLoop()():
        b = reader.read()
        EUDBreakIf(b == 0)
        if EUDIf()([writing_line == 1, b == ord('\n')]):
            writer.write_f("...")
            EUDBreak()
        EUDEndIf()

        if EUDIfNot()(b == 0xD):
            if EUDIfNot()(b == ord('\n')):
                writing_line << 1
                writer.write(b)
            EUDEndIf()
        EUDEndIf()
    EUDEndInfLoop()

def _set_string_id(new_string_id):
    if EUDIf()([new_string_id >= 1, new_string_id <= string_count]):
        cur_string_id << new_string_id
    EUDEndIf()

class StringManagerApp(Application):
    @staticmethod
    def set_return(result_var):
        assert IsEUDVariable(result_var)
        v_result_epd << EPD(result_var.getValueAddr())
        _set_string_id(result_var)

    def on_destruct(self):
        if EUDIfNot()(v_result_epd == EPD(0)):
            f_dwwrite_epd(v_result_epd, cur_string_id)
        EUDEndIf()
        v_result_epd << EPD(0)

    def loop(self):
        if EUDIf()(app_manager.key_press("ESC")):
            app_manager.request_destruct()
            EUDReturn()
        if EUDElseIf()(app_manager.key_press("F7")):
            _set_string_id(cur_string_id - 1)
        if EUDElseIf()(app_manager.key_press("F8")):
            _set_string_id(cur_string_id + 1)
        if EUDElseIf()(app_manager.key_press("E", hold=["LCTRL"])):
            from .editor import StringEditorApp
            app_manager.start_application(StringEditorApp)
        if is_bridge_mode():
            if EUDElseIf()(app_manager.key_press("B", hold=["LCTRL"])):
                from .exporter import StringExporterApp
                app_manager.start_application(StringExporterApp)
        if EUDElseIf()(app_manager.key_press("F", hold=["LCTRL"])):
            from .search import StringSearchApp
            StringSearchApp.set_return_epd(EPD(cur_string_id.getValueAddr()))
            app_manager.start_application(StringSearchApp)
        EUDEndIf()
        app_manager.request_update()

    def print(self, writer):
        writer.write_f("\x04StringManager id=%D / total %D strings\n", cur_string_id, string_count)
        _write_first_line(STRSection + f_dwread_epd(STRSection_epd + cur_string_id))
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
        _set_string_id(new_string_id)
