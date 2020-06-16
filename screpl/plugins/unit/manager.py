from eudplib import *

from screpl.core.application import Application

from . import app_manager

# app-specific initializing arguments
_unitid = EUDVariable(0)
_resultref_unitid_epd = EUDVariable(EPD(0))

DISP_MAIN = 0
DISP_MANUAL = 1
v_display_mode = EUDVariable()

'''
unitid
0-227 (normal units)
228 None
229 (any unit)
230 (men)
231 (buildings)
232 (factories)
'''

@EUDTypedFunc([TrgPlayer, None, None, None])
def _create_unit(playerid, unitid, x, y):
    epds = [EPD(0x58DC60)+t for t in range(4)]
    orig_values = [f_dwread_epd(epd) for epd in epds]

    f_dwwrite_epd(epds[0], x)
    f_dwwrite_epd(epds[1], y)
    f_dwwrite_epd(epds[2], x)
    f_dwwrite_epd(epds[3], y)

    DoActions(CreateUnit(1, unitid, 1, playerid))

    for epd, value in zip(epds, orig_values):
        f_dwwrite_epd(epd, value)

class UnitManagerApp(Application):
    fields = [
        "unitid",
        "resultref_unitid_epd", # unitid of chosen unit
    ]

    @staticmethod
    def set_content(unitid, resultref_unitid_epd=None):
        # set initializing arguments
        _unitid << unitid
        if resultref_unitid_epd:
            _resultref_unitid_epd << resultref_unitid_epd

    def on_init(self):
        self.unitid = 0
        self.resultref_unitid_epd = _resultref_unitid_epd

        self.focus_unit_id(_unitid)

        v_display_mode << DISP_MAIN

        # restore initializing arguments
        _resultref_unitid_epd << EPD(0)

    def on_destruct(self):
        unitid = self.unitid
        resultref_unitid_epd = self.resultref_unitid_epd
        if EUDIfNot()(resultref_unitid_epd == EPD(0)):
            f_dwwrite_epd(resultref_unitid_epd, unitid)
        EUDEndIf()
        _unitid << unitid

    def focus_unit_id(self, new_unitid):
        Trigger(
            conditions=new_unitid.AtLeast(0x80000000),
            actions=new_unitid.SetNumber(0)
        )
        Trigger(
            conditions=new_unitid.AtLeast(233),
            actions=new_unitid.SetNumber(232)
        )
        if EUDIfNot()(new_unitid == self.unitid):
            self.unitid = new_unitid
            app_manager.request_update()
        EUDEndIf()

    def loop(self):
        unitid = self.unitid
        hold_ctrl = app_manager.key_holdcounter("LCTRL")
        mouse_pos = app_manager.get_mouse_position()
        selunit_epd = f_epdread_epd(EPD(0x6284B8))

        if EUDIf()(app_manager.key_press("ESC")):
            app_manager.request_destruct()
        if EUDElseIf()(app_manager.key_down("F1")):
            v_display_mode << DISP_MANUAL
            app_manager.request_update()
        if EUDElseIf()(app_manager.key_up("F1")):
            v_display_mode << DISP_MAIN
            app_manager.request_update()
        if EUDElseIf()(app_manager.key_press("F7", sync=[hold_ctrl])):
            self.focus_unit_id(unitid - EUDTernary(hold_ctrl)(8)(1))
        if EUDElseIf()(app_manager.key_press("F8", sync=[hold_ctrl])):
            self.focus_unit_id(unitid + EUDTernary(hold_ctrl)(8)(1))
        if EUDElseIf()(app_manager.key_press("1", sync=mouse_pos)):
            _create_unit(P1, unitid, mouse_pos[0], mouse_pos[1])
        if EUDElseIf()(app_manager.key_press("2", sync=mouse_pos)):
            _create_unit(P2, unitid, mouse_pos[0], mouse_pos[1])
        if EUDElseIf()(app_manager.key_press("3", sync=mouse_pos)):
            _create_unit(P3, unitid, mouse_pos[0], mouse_pos[1])
        if EUDElseIf()(app_manager.key_press("4", sync=mouse_pos)):
            _create_unit(P4, unitid, mouse_pos[0], mouse_pos[1])
        if EUDElseIf()(app_manager.key_press("5", sync=mouse_pos)):
            _create_unit(P5, unitid, mouse_pos[0], mouse_pos[1])
        if EUDElseIf()(app_manager.key_press("6", sync=mouse_pos)):
            _create_unit(P6, unitid, mouse_pos[0], mouse_pos[1])
        if EUDElseIf()(app_manager.key_press("7", sync=mouse_pos)):
            _create_unit(P7, unitid, mouse_pos[0], mouse_pos[1])
        if EUDElseIf()(app_manager.key_press("8", sync=mouse_pos)):
            _create_unit(P8, unitid, mouse_pos[0], mouse_pos[1])
        if EUDElseIf()(app_manager.key_press("DELETE", sync=[selunit_epd])):
            if EUDIfNot()(selunit_epd == EPD(0)):
                DoActions(SetMemoryXEPD(selunit_epd + 0x4C//4,
                                        SetTo, 0, 0xFF00))
            EUDEndIf()
        EUDEndIf()

    def print(self, writer):
        if EUDIf()(v_display_mode == DISP_MAIN):
            writer.write_f("\x16Unit Manager. Press F1 to get manual\n")

            target_unitid = self.unitid

            cur, until = EUDCreateVariables(2)
            if EUDIf()(target_unitid == 232):
                cur << 232
                until << 232 + 1
            if EUDElse()():
                quot, mod = f_div(target_unitid, 8)
                cur << quot * 8
                until << cur + 8
            EUDEndIf()

            # fill contents
            written_point = Forward()
            if EUDInfLoop()():
                EUDBreakIf(cur >= until)

                if EUDIf()(cur == target_unitid):
                    writer.write(0x11) # orange
                if EUDElse()():
                    writer.write(0x02) # pale blue
                EUDEndIf()

                writer.write_f(" %D: ", cur)
                writer.write_unit(cur)
                writer.write(ord('\n'))

                DoActions(cur.AddNumber(1))
            EUDEndInfLoop()
        if EUDElse()():
            writer.write_f(
                "\x16Unit Manager Manual\n"
                "Press ESC to destroy the unit manager\n"
                "Press F7/F8 to change focus\n"
                "Press F7/F8 with holding CTRL key to move focus at page level\n"
                "Press 1, 2, ..., 8 to create focused unit on mouse cursor\n"
                "Press DELETE to kill selected unit\n")
        EUDEndIf()
        writer.write(0)
