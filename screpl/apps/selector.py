from eudplib import *

import screpl.core.application as application
import screpl.resources.table.tables as tb
import screpl.main as main
import screpl.utils.referencetable as referencetable

# number of items to show in a page
NITEMS = 8

def _createapp(domainname, reftable):
    reftable_sz = len(reftable._dict)
    _value = EUDVariable(0)
    _offset = EUDVariable(0)
    _result_epd = EUDVariable(0)


    @EUDFunc
    def focus_offset(new_offset):
        Trigger(
            conditions=new_offset.AtLeast(0x80000000),
            actions=new_offset.SetNumber(0)
        )
        Trigger(
            conditions=new_offset.AtLeast(reftable_sz),
            actions=new_offset.SetNumber(reftable_sz - 1)
        )
        if EUDIfNot()(new_offset == _offset):
            _offset << new_offset
            _value << f_dwread_epd((EPD(reftable)+2) + 2*new_offset)
            main.get_app_manager().request_update()
        EUDEndIf()

    class _SelectorApp(application.Application):
        @staticmethod
        def setContent(default, result_epd=None):
            _value << default
            if result_epd:
                _result_epd << result_epd

        def on_init(self):
            _offset << 0
            def func(i, name_epd, value_epd):
                if EUDIf()(MemoryEPD(value_epd, Exactly, _value)):
                    _offset << i
                    EUDReturn()
                EUDEndIf()

            referencetable.ReferenceTable.iter_table(EPD(reftable), func)

            # failed on search
            _value << 0

        def on_destruct(self):
            if EUDIfNot()(_result_epd == 0):
                f_dwwrite_epd(_result_epd, _value)
                _result_epd << 0
            EUDEndIf()

        def loop(self):
            app_manager = main.get_app_manager()
            if EUDIf()(app_manager.key_press("ESC")):
                app_manager.request_destruct()
            if EUDElseIf()(app_manager.key_press("F7", hold=["LCTRL"])):
                focus_offset(_offset - NITEMS)
            if EUDElseIf()(app_manager.key_press("F7")):
                focus_offset(_offset - 1)
            if EUDElseIf()(app_manager.key_press("F8", hold=["LCTRL"])):
                focus_offset(_offset + NITEMS)
            if EUDElseIf()(app_manager.key_press("F8")):
                focus_offset(_offset + 1)
            EUDEndIf()
            app_manager.request_update()

        def print(self, writer):
            writer.write_f(
                "\x16{} Selector, value=%D, ESC, F7, F8\n".format(domainname),
                _value)

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


AIScriptSelectorApp     = _createapp("AIScript",     tb.AIScript)
ModifierSelectorApp     = _createapp("Modifier",     tb.Modifier)
AllyStatusSelectorApp   = _createapp("AllyStatus",   tb.AllyStatus)
ComparisonSelectorApp   = _createapp("Comparison",   tb.Comparison)
OrderSelectorApp        = _createapp("Order",        tb.Order)
PlayerSelectorApp       = _createapp("Player",       tb.Player)
PropStateSelectorApp    = _createapp("PropState",    tb.PropState)
ResourceSelectorApp     = _createapp("Resource",     tb.Resource)
ScoreSelectorApp        = _createapp("Score",        tb.Score)
SwitchActionSelectorApp = _createapp("SwitchAction", tb.SwitchAction)
SwitchStateSelectorApp  = _createapp("SwitchState",  tb.SwitchState)