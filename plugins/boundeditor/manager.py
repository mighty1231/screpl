from eudplib import *

from repl import Application, AppCommand
from . import appManager, superuser
from .option import OptionApp
from .pattern import PatternApp
from .testmode import TestPatternApp

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
        EUDEndIf()

    def print(self, writer):
        writer.write_f("\x16Bound Editor Manager\n")
        writer.write_f("LCTRL + O: Option\n")
        writer.write_f("LCTRL + P: Pattern\n")
        writer.write_f("LCTRL + T: Test\n")
        writer.write_f("Chat maphack() to turn on maphack\n")
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

