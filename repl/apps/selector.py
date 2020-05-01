from eudplib import *
from repl import (
    Application,
    getAppManager,
    ReferenceTable,
)

# number of items to show in a page
NITEMS = 8

def _createapp(domainname, reftable):
    reftable_sz = len(reftable._dict)
    _value = EUDVariable(0)
    _offset = EUDVariable(0)
    _result_epd = EUDVariable(0)


    @EUDFunc
    def focusOffset(new_offset):
        Trigger(
            conditions = new_offset.AtLeast(0x80000000),
            actions = new_offset.SetNumber(0)
        )
        Trigger(
            conditions = new_offset.AtLeast(reftable_sz),
            actions = new_offset.SetNumber(reftable_sz - 1)
        )
        if EUDIfNot()(new_offset == _offset):
            _offset << new_offset
            _value << f_dwread_epd((EPD(reftable)+2) + 2*new_offset)
            getAppManager().requestUpdate()
        EUDEndIf()

    class _SelectorApp(Application):
        @staticmethod
        def setContent(default, result_epd = None):
            _value << default
            if result_epd:
                _result_epd << result_epd

        def onInit(self):
            _offset << 0
            def func(i, name_epd, value_epd):
                if EUDIf()(MemoryEPD(value_epd, Exactly, _value)):
                    _offset << i
                    EUDReturn()
                EUDEndIf()

            ReferenceTable.Iter(EPD(reftable), func)

            # failed on search
            _value << 0

        def onDestruct(self):
            if EUDIfNot()(_result_epd == 0):
                f_dwwrite_epd(_result_epd, _value)
                _result_epd << 0
            EUDEndIf()

        def loop(self):
            appManager = getAppManager()
            if EUDIf()(appManager.keyPress("ESC")):
                appManager.requestDestruct()
            if EUDElseIf()(appManager.keyPress("F7", hold=["LCTRL"])):
                focusOffset(_offset - NITEMS)
            if EUDElseIf()(appManager.keyPress("F7")):
                focusOffset(_offset - 1)
            if EUDElseIf()(appManager.keyPress("F8", hold=["LCTRL"])):
                focusOffset(_offset + NITEMS)
            if EUDElseIf()(appManager.keyPress("F8")):
                focusOffset(_offset + 1)
            EUDEndIf()
            appManager.requestUpdate()

        def print(self, writer):
            writer.write_f("\x16{} Selector, value=%D, ESC, F7, F8\n".format(domainname),
                _value, _offset)

            cur, until, pageend, key_epd = EUDCreateVariables(4)
            if EUDIf()(_offset >= (reftable_sz // NITEMS * NITEMS)):
                DoActions([
                    cur.SetNumber(reftable_sz // NITEMS * NITEMS),
                    until.SetNumber(reftable_sz),
                    pageend.SetNumber((reftable_sz // NITEMS * NITEMS) + NITEMS),
                    key_epd.SetNumber(EPD(reftable) + (reftable_sz // NITEMS * NITEMS) * 2 + 1)
                ])
            if EUDElse()():
                quot, mod = f_div(_offset, NITEMS)
                cur << quot * NITEMS
                until << cur + NITEMS
                pageend << until
                key_epd << (EPD(reftable) + 1) + cur * 2 
            EUDEndIf()

            # print contents
            if EUDInfLoop()():
                EUDBreakIf(cur >= until)

                if EUDIf()(cur == _offset):
                    writer.write(0x11) # orange
                if EUDElse()():
                    writer.write(0x02) # pale blue
                EUDEndIf()

                writer.write_f(" %E\n", f_dwread_epd(key_epd))

                DoActions([
                    cur.AddNumber(1),
                    key_epd.AddNumber(2)
                ])
            EUDEndInfLoop()

            # print spaces
            if EUDInfLoop()():
                EUDBreakIf(cur >= pageend)
                writer.write(ord('\n'))
                cur += 1
            EUDEndInfLoop()

            writer.write(0)

    return _SelectorApp

from ..resources.table.tables import (
    tb_AIScript,
    tb_Modifier,
    tb_AllyStatus,
    tb_Comparison,
    tb_Order,
    tb_Player,
    tb_PropState,
    tb_Resource,
    tb_Score,
    tb_SwitchAction,
    tb_SwitchState
)

AIScriptSelectorApp     = _createapp("AIScript",     tb_AIScript)
ModifierSelectorApp     = _createapp("Modifier",     tb_Modifier)
AllyStatusSelectorApp   = _createapp("AllyStatus",   tb_AllyStatus)
ComparisonSelectorApp   = _createapp("Comparison",   tb_Comparison)
OrderSelectorApp        = _createapp("Order",        tb_Order)
PlayerSelectorApp       = _createapp("Player",       tb_Player)
PropStateSelectorApp    = _createapp("PropState",    tb_PropState)
ResourceSelectorApp     = _createapp("Resource",     tb_Resource)
ScoreSelectorApp        = _createapp("Score",        tb_Score)
SwitchActionSelectorApp = _createapp("SwitchAction", tb_SwitchAction)
SwitchStateSelectorApp  = _createapp("SwitchState",  tb_SwitchState)
