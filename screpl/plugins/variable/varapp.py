from eudplib import *

from screpl.apps.scroll import ScrollApp

from . import condition_writer, watched_eud_vars

total_size = watched_eud_vars.size() + condition_writer.funcptr_len

class VariableApp(ScrollApp):
    fields = []

    def write_title(self, writer):
        writer.write_f(
            "Variable App. Shows exact values of P1~P8. "
            "press F7 or F8 to navigate")

    def write_line(self, writer, line):
        if EUDIf()(line <= condition_writer.funcptr_len-1):
            writer.write_f("\x16 %D: ", line + 1)
            EUDFuncPtr(0, 0)(condition_writer.funcptr_arr[line])()
        if EUDElse()():
            if EUDIf()(line == condition_writer.funcptr_len):
                writer.write_f("\x1E-----------------")
                EUDReturn()
            EUDEndIf()
            line -= (condition_writer.funcptr_len + 1)

            tmp = line * 2
            varaddr_epd = f_dwread_epd((EPD(watched_eud_vars)+1) + tmp)
            var_value = f_dwread_epd((EPD(watched_eud_vars)+2) + tmp)

            writer.write_f("\x1E * %E: %H = %D",
                           varaddr_epd,
                           f_dwread_epd(var_value),
                           f_dwread_epd(var_value))
        EUDEndIf()

    def get_line_count(self):
        EUDReturn(total_size + 1)
