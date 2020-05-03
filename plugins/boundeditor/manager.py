from eudplib import *

from repl import Application, AppCommand
from . import appManager, superuser
from .option import OptionApp
from .pattern import PatternApp
from .testmode import TestPatternApp
from .exporter import ExporterApp

def deleteSelectedUnit():
    # 0x6284B8  CurrentUnitSelection     CUNIT *CurrentUnitSelection[12]
    # 0x6284E8  AllPlayerSelectionGroups CUNIT *AllPlayerSelectionGroups[8][12]

    # use location 1
    le = EPD(0x58DC60)
    te = EPD(0x58DC60) + 1
    re = EPD(0x58DC60) + 2
    be = EPD(0x58DC60) + 3
    lv, tv, rv, bv = [f_dwread_epd(ee) for ee in [le, te, re, be]]

    i = EUDVariable()
    i << 0
    if EUDInfLoop()():
        EUDBreakIf(i >= 12)

        cu_epd = f_epdread_epd(EPD(0x6284B8))
        EUDBreakIf(cu_epd == EPD(0))

        player_id = f_bread_epd(cu_epd + (0x4C//4), 0)
        unit_type = f_wread_epd(cu_epd + (0x64//4), 0)
        pos_x = f_wread_epd(cu_epd + (0x28//4), 0)
        pos_y = f_wread_epd(cu_epd + (0x28//4), 2)

        DoActions([
            SetMemoryEPD(le, SetTo, pos_x),
            SetMemoryEPD(te, SetTo, pos_y),
            SetMemoryEPD(re, SetTo, pos_x),
            SetMemoryEPD(be, SetTo, pos_y),
            RemoveUnitAt(All, unit_type, 1, player_id)
        ])
        i += 1
    EUDEndInfLoop()


    # restore location 1
    for ee, vv in zip([le, te, re, be], [lv, tv, rv, bv]):
        f_dwwrite_epd(ee, vv)



class BoundManagerApp(Application):
    def loop(self):
        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
            EUDReturn()
        if EUDElseIf()(appManager.keyPress("O", hold=["LCTRL"])):
            appManager.startApplication(OptionApp)
        if EUDElseIf()(appManager.keyPress("P", hold=["LCTRL"])):
            appManager.startApplication(PatternApp)
        if EUDElseIf()(appManager.keyPress("T", hold=["LCTRL"])):
            appManager.startApplication(TestPatternApp)
        if appManager.isBridgeMode():
            if EUDElseIf()(appManager.keyPress("E", hold=["LCTRL"])):
                appManager.startApplication(ExporterApp)
        if EUDElseIf()(appManager.keyPress("delete")):
            deleteSelectedUnit()
        EUDEndIf()

    def print(self, writer):
        writer.write_f("\x16Bound Editor Manager\n")
        writer.write_f("LCTRL + O: Option\n")
        writer.write_f("LCTRL + P: Pattern\n")
        writer.write_f("LCTRL + T: Test\n")
        if appManager.isBridgeMode():
            writer.write_f("LCTRL + E: Exporter\n")
        writer.write_f("Chat maphack() to turn on maphack\n")
        writer.write_f("Press DELETE key to remove selected units\n")
        writer.write(0)

    @AppCommand([])
    def maphack(self):
        le = EPD(0x58DC60)
        te = EPD(0x58DC60) + 1
        re = EPD(0x58DC60) + 2
        be = EPD(0x58DC60) + 3

        lv, tv, rv, bv = [f_dwread_epd(ee) for ee in [le, te, re, be]]

        mapw = appManager.getMapWidth()
        maph = appManager.getMapHeight()

        actions = []
        for y in range(256, maph * 32, 512):
            actions.append(SetMemoryEPD(te, SetTo, y))
            actions.append(SetMemoryEPD(be, SetTo, y))

            for x in range(256, mapw * 32, 512):
                actions.append(SetMemoryEPD(le, SetTo, x))
                actions.append(SetMemoryEPD(re, SetTo, x))
                actions.append(CreateUnit(1, "Map Revealer", 1, superuser))
        DoActions(actions)

        for ee, vv in zip([le, te, re, be], [lv, tv, rv, bv]):
            f_dwwrite_epd(ee, vv)

