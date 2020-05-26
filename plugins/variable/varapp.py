from eudplib import *

from screpl.apps.scroll import ScrollApp
from screpl.utils.referencetable import ReferenceTable
from screpl.core.appcommand import AppCommand
from screpl.core.appmethod import AppTypedMethod
from screpl.writer import write_unit

from . import death_units, watched_eud_vars, accessed_resources

watched_eud_vars_size = EUDVariable()

class VariableApp(ScrollApp):
    fields = []

    def on_init(self):
        ScrollApp.on_init(self)
        watched_eud_vars_size << ReferenceTable.get_size(EPD(watched_eud_vars))

    def write_title(self, writer):
        writer.write_f("Variable App. press F7 or F8. ( Offset = %D )", self.offset)

    def write_line(self, writer, line):
        # Ore / Gas
        if accessed_resources:
            if EUDIf()(line == 0):
                writer.write_f("\x1e[Resource]")
                EUDReturn()
            EUDEndIf()
            line -= 1

            if Ore in accessed_resources:
                if EUDIf()(line == 0):
                    writer.write_f("\x1e * Ore")
                    self.write_pvar_from_epd(EPD(0x57F0F0))
                EUDEndIf()
                line -= 1
            if Gas in accessed_resources:
                if EUDIf()(line == 0):
                    writer.write_f("\x1e * Gas")
                    self.write_pvar_from_epd(EPD(0x57F120))
                EUDEndIf()
                line -= 1

        # Death units
        if death_units:
            if EUDIf()(line == 0):
                writer.write_f("\x1e[Deaths]")
                EUDReturn()
            EUDEndIf()
            line -= 1

            for i, unitID in enumerate(death_units):
                if EUDIf()(line == 0):
                    # write number
                    writer.write_f("\x1e # {} ".format(i+1))

                    # write unit name
                    write_unit(unitID)

                    # write death values
                    self.write_pvar_from_epd(EPD(0x58A364 + 48*unitID))
                    EUDReturn()
                EUDEndIf()
                line -= 1

        # EUDVariables
        if EUDIf()(line == 0):
            writer.write_f("\x1e[EUDVariable]")
            EUDReturn()
        EUDEndIf()
        line -= 1

        if EUDIf()(line >= watched_eud_vars_size):
            EUDReturn()
        EUDEndIf()

        tmp = line * 2
        varaddr_epd = f_dwread_epd((EPD(watched_eud_vars)+1) + tmp)
        var_value = f_dwread_epd((EPD(watched_eud_vars)+2) + tmp)

        writer.write_f("\x1e * %E: %H = %D",
            varaddr_epd,
            f_dwread_epd(var_value),
            f_dwread_epd(var_value)
        )

    @AppTypedMethod([None], [], with_main_writer = True)
    def write_pvar_from_epd(self, writer, epd):
        writer.write_f(" : \x08%D", f_dwread_epd(epd))
        writer.write_f("\x1e / \x0e%D", f_dwread_epd(epd + 1))
        writer.write_f("\x1e / \x0f%D", f_dwread_epd(epd + 2))
        writer.write_f("\x1e / \x10%D", f_dwread_epd(epd + 3))
        writer.write_f("\x1e / \x11%D", f_dwread_epd(epd + 4))
        writer.write_f("\x1e / \x15%D", f_dwread_epd(epd + 5))
        writer.write_f("\x1e / \x16%D", f_dwread_epd(epd + 6))
        writer.write_f("\x1e / \x17%D", f_dwread_epd(epd + 7))


    def get_line_count(self):
        ret = 0
        if accessed_resources:
            ret += 1 + len(accessed_resources)
        if death_units:
            ret += 1 + len(death_units)
        if EUDIf()(watched_eud_vars_size == 0):
            EUDReturn(ret)
        if EUDElse()():
            ret += 1 + watched_eud_vars_size
        EUDEndIf()
        EUDReturn(ret)