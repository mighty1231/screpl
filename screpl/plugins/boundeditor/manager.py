from eudplib import *

from screpl.core.appcommand import AppCommand
from screpl.core.application import Application

from screpl.main import is_bridge_mode

from . import app_manager, su_id
from .option import OptionApp
from .pattern import PatternApp
from .testmode import TestPatternApp
from .exporter import ExporterApp

def delete_selected_units():
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
        if EUDIf()(app_manager.key_press("ESC")):
            app_manager.request_destruct()
        if EUDElseIf()(app_manager.key_press("O", hold=["LCTRL"])):
            app_manager.start_application(OptionApp)
        if EUDElseIf()(app_manager.key_press("P", hold=["LCTRL"])):
            app_manager.start_application(PatternApp)
        if EUDElseIf()(app_manager.key_press("T", hold=["LCTRL"])):
            app_manager.start_application(TestPatternApp)
        if is_bridge_mode():
            if EUDElseIf()(app_manager.key_press("E", hold=["LCTRL"])):
                app_manager.start_application(ExporterApp)
        if EUDElseIf()(app_manager.key_press("delete")):
            delete_selected_units()
        EUDEndIf()

    def print(self, writer):
        writer.write_f("\x16Bound Editor Manager\n")
        writer.write_f("LCTRL + O: Option\n")
        writer.write_f("LCTRL + P: Pattern\n")
        writer.write_f("LCTRL + T: Test\n")
        if is_bridge_mode():
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

        mapw = app_manager.get_map_width()
        maph = app_manager.get_map_height()

        actions = []
        for y in range(256, maph * 32, 512):
            actions.append(SetMemoryEPD(te, SetTo, y))
            actions.append(SetMemoryEPD(be, SetTo, y))

            for x in range(256, mapw * 32, 512):
                actions.append(SetMemoryEPD(le, SetTo, x))
                actions.append(SetMemoryEPD(re, SetTo, x))
                actions.append(CreateUnit(1, "Map Revealer", 1, su_id))
        DoActions(actions)

        for ee, vv in zip([le, te, re, be], [lv, tv, rv, bv]):
            f_dwwrite_epd(ee, vv)

