from eudplib import *

from repl import Application
from . import appManager

from repl.resources.unitname import EUDGetDefaultUnitName_epd
from repl.resources.offset import off_unitsdat_UnitMapString

# app-specific initializing arguments
_unitid = EUDVariable(0)
_result_unitid = EUDVariable(0)

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
        "result_unitid", # unitid of chosen unit
    ]

    @staticmethod
    def setContent(unitid, result_unitid = None):
        # set initializing arguments
        _unitid << unitid
        if result_unitid:
            _result_unitid << result_unitid

    def onInit(self):
        self.unitid = 0
        self.result_unitid = _result_unitid

        self.focusUnitID(_unitid)

        # restore initializing arguments
        _result_unitid << 0

    def onDestruct(self):
        unitid = self.unitid
        result_unitid = self.result_unitid
        if EUDIfNot()(result_unitid == 0):
            f_dwwrite_epd(result_unitid, unitid)
        EUDEndIf()
        _unitid << unitid

    def focusUnitID(self, new_unitid):
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
            appManager.requestUpdate()
        EUDEndIf()

    def loop(self):
        unitid = self.unitid
        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
            EUDReturn()
        if EUDElseIf()(appManager.keyPress("F7", hold=["LCTRL"])):
            self.focusUnitID(unitid - 8)
        if EUDElseIf()(appManager.keyPress("F7")):
            self.focusUnitID(unitid - 1)
        if EUDElseIf()(appManager.keyPress("F8", hold=["LCTRL"])):
            self.focusUnitID(unitid + 8)
        if EUDElseIf()(appManager.keyPress("F8")):
            self.focusUnitID(unitid + 1)
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
            if EUDIf()(cur <= 227):
                stringid = off_unitsdat_UnitMapString.read(cur)

                if EUDIfNot()(stringid == 0):
                    writer.write_STR_string(stringid)
                    EUDJump(written_point)
                EUDEndIf()
            EUDEndIf()
            writer.write_f("%E", EUDGetDefaultUnitName_epd(cur))

            written_point << NextTrigger()
            writer.write(ord('\n'))

            DoActions(cur.AddNumber(1))
        EUDEndInfLoop()

        branch << RawTrigger()
        branch_last << NextTrigger()
        writer.write_f("\n" * 7)

        branch_common << NextTrigger()
        writer.write(0)
