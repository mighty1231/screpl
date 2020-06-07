from eudplib import *

from screpl.core.application import Application

from . import app_manager

# app-specific initializing arguments
_unitid = EUDVariable(0)
_resultref_unitid_epd = EUDVariable(EPD(0))

'''
unitid
0-227 (normal units)
228 None
229 (any unit)
230 (men)
231 (buildings)
232 (factories)
'''

class UnitManagerApp(Application):
    fields = [
        "unitid",
        "resultref_unitid_epd", # unitid of chosen unit
    ]

    @staticmethod
    def set_content(unitid, resultref_unitid_epd = None):
        # set initializing arguments
        _unitid << unitid
        if resultref_unitid_epd:
            _resultref_unitid_epd << resultref_unitid_epd

    def on_init(self):
        self.unitid = 0
        self.resultref_unitid_epd = _resultref_unitid_epd

        self.focus_unit_id(_unitid)

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
            conditions = new_unitid.AtLeast(0x80000000),
            actions = new_unitid.SetNumber(0)
        )
        Trigger(
            conditions = new_unitid.AtLeast(233),
            actions = new_unitid.SetNumber(232)
        )
        if EUDIfNot()(new_unitid == self.unitid):
            self.unitid = new_unitid
            app_manager.request_update()
        EUDEndIf()

    def loop(self):
        unitid = self.unitid
        if EUDIf()(app_manager.key_press("ESC")):
            app_manager.request_destruct()
            EUDReturn()
        if EUDElseIf()(app_manager.key_press("F7", hold=["LCTRL"])):
            self.focus_unit_id(unitid - 8)
        if EUDElseIf()(app_manager.key_press("F7")):
            self.focus_unit_id(unitid - 1)
        if EUDElseIf()(app_manager.key_press("F8", hold=["LCTRL"])):
            self.focus_unit_id(unitid + 8)
        if EUDElseIf()(app_manager.key_press("F8")):
            self.focus_unit_id(unitid + 1)
        EUDEndIf()

    def print(self, writer):
        writer.write_f("\x16Unit Manager\n")

        target_unitid = self.unitid

        branch, branch_common, branch_last = [Forward() for _ in range(3)]
        cur, until = EUDCreateVariables(2)
        if EUDIf()(target_unitid == 232):
            cur << 232
            until << 232 + 1
            DoActions(SetNextPtr(branch, branch_last))
        if EUDElse()():
            quot, mod = f_div(target_unitid, 8)
            cur << quot * 8
            until << cur + 8
            DoActions(SetNextPtr(branch, branch_common))
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

        branch << RawTrigger()
        branch_last << NextTrigger()
        writer.write_f("\n" * 7)

        branch_common << NextTrigger()
        writer.write(0)

