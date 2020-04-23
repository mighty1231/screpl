from eudplib import *
from repl import ScrollApp, ReferenceTable

from repl.resources.offset import off_unitsdat_UnitMapString
from repl.resources.unitname import getDefaultUnitName
from . import manager, death_units, watched_eud_vars

watched_eud_vars_size = EUDVariable()

class VariableApp(ScrollApp):
    fields = []

    def onInit(self):
        watched_eud_vars_size << ReferenceTable.GetSize(EPD(watched_eud_vars))

    def writeTitle(self, writer):
        writer.write_f("Variable App")

    def writeLine(self, writer, line):
        if EUDIf()(line == 0):
            writer.write_f("1. Death")
        for i, unitID in enumerate(death_units):
            EUDElseIf()(line == (i+1))

            # write number
            writer.write_f("\x1e# {} ".format(i+1))

            # write unit name
            strID = off_unitsdat_UnitMapString.read(unitID)
            if EUDIf()(strID == 0):
                writer.write_f(getDefaultUnitName(i))
            if EUDElse()():
                writer.write_STR_string(strID)
            EUDEndIf()

            # write death values of each players
            writer.write_f(" : \x08%D", f_dwread_epd(EPD(0x58A364 + 48*unitID)))
            writer.write_f("\x1e / \x0e%D", f_dwread_epd(EPD(0x58A364 + 48*unitID + 4*1)))
            writer.write_f("\x1e / \x0f%D", f_dwread_epd(EPD(0x58A364 + 48*unitID + 4*2)))
            writer.write_f("\x1e / \x10%D", f_dwread_epd(EPD(0x58A364 + 48*unitID + 4*3)))
            writer.write_f("\x1e / \x11%D", f_dwread_epd(EPD(0x58A364 + 48*unitID + 4*4)))
            writer.write_f("\x1e / \x15%D", f_dwread_epd(EPD(0x58A364 + 48*unitID + 4*5)))
            writer.write_f("\x1e / \x16%D", f_dwread_epd(EPD(0x58A364 + 48*unitID + 4*6)))
            writer.write_f("\x1e / \x17%D", f_dwread_epd(EPD(0x58A364 + 48*unitID + 4*7)))

        if EUDElseIf()(line == (len(death_units) + 2)):
            writer.write_f("\x1e2. EUDVariable")
        if EUDElse()():
            idx = line - (len(death_units) + 3)
            if EUDIf()(idx >= watched_eud_vars_size):
                EUDReturn()
            EUDEndIf()

            tmp = idx * 2
            varaddr_epd = f_dwread_epd((EPD(watched_eud_vars)+1) + tmp)
            var_value = f_dwread_epd((EPD(watched_eud_vars)+2) + tmp)

            writer.write_f("\x1e * %E: %H = %D",
            # writer.write_f(" * %H = %D",
                varaddr_epd,
                f_dwread_epd(var_value),
                f_dwread_epd(var_value)
            )
        EUDEndIf()

    def getLineCount(self):
        return (1 + len(death_units) + 2) + watched_eud_vars_size
