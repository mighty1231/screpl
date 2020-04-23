from eudplib import *
from repl import (
    Application,
    AppTypedMethod,
    AppCommand,
    argEncNumber,
    ScrollApp
)

from repl.resources.offset import off_unitsdat_UnitMapString
from repl.resources.unitname import getDefaultUnitName
from . import manager, death_units

class VariableApp(ScrollApp):
    fields = []

    def writeTitle(self, writer):
        writer.write_f("Variable App")

    def writeLine(self, writer, line):
        if EUDIf()(line == 0):
            writer.write_f("Death Variables")
        for i, unitID in enumerate(death_units):
            EUDElseIf()(line == (i+1))

            # write number
            writer.write_f("# {} ".format(i+1))

            # write unit name
            strID = off_unitsdat_UnitMapString.read(unitID)
            if EUDIf()(strID == 0):
                writer.write_f(getDefaultUnitName(i))
            if EUDElse()():
                writer.write_STR_string(strID)
            EUDEndIf()

            # write death values of each players
            writer.write_f(" : %D", f_dwread_epd(EPD(0x58A364 + 48*unitID)))
            writer.write_f(" / %D", f_dwread_epd(EPD(0x58A364 + 48*unitID + 4*1)))
            writer.write_f(" / %D", f_dwread_epd(EPD(0x58A364 + 48*unitID + 4*2)))
            writer.write_f(" / %D", f_dwread_epd(EPD(0x58A364 + 48*unitID + 4*3)))
            writer.write_f(" / %D", f_dwread_epd(EPD(0x58A364 + 48*unitID + 4*4)))
            writer.write_f(" / %D", f_dwread_epd(EPD(0x58A364 + 48*unitID + 4*5)))
            writer.write_f(" / %D", f_dwread_epd(EPD(0x58A364 + 48*unitID + 4*6)))
            writer.write_f(" / %D", f_dwread_epd(EPD(0x58A364 + 48*unitID + 4*7)))
        EUDEndIf()

    def getLineCount(self):
        return 1 + len(death_units)
