"""SelectorApp"""
from eudplib import *

import screpl.core.application as application
import screpl.main as main
import screpl.utils.referencetable as rt

# number of items to show in a page
ENTRY_COUNT_PER_PAGE = 8

_reftable_sz = EUDVariable()
_reftable_epd = EUDVariable()
_value = EUDVariable()
_index = EUDVariable()
_result_epd = EUDVariable(EPD(0))

DISPMODE_MAIN = 0
DISPMODE_MANUAL = 1
_dispmode = EUDVariable()

@EUDFunc
def _focus_index(new_index):
    Trigger(
        conditions=new_index.AtLeast(0x80000000),
        actions=new_index.SetNumber(0)
    )
    Trigger(
        conditions=new_index.AtLeast(_reftable_sz),
        actions=new_index.SetNumber(_reftable_sz - 1)
    )
    if EUDIfNot()(new_index == _index):
        _index << new_index
        _value << f_dwread_epd((_reftable_epd+2) + 2*new_index)
        main.get_app_manager().request_update()
    EUDEndIf()

class SelectorApp(application.Application):
    @staticmethod
    def set_content(reftable, variable):
        """Set initializing argument before start the app

        Set the contents and address to write the result value

        Args:
            reftable(ReferenceTable): ReferenceTable object with pairs of
                epd-type strings and numerical values.
            variable(EUDVariable): the default value to set and where the
                result value will be saved into
        """
        assert isinstance(reftable, rt.ReferenceTable)
        assert IsEUDVariable(variable)

        _reftable_epd << EPD(reftable)
        _reftable_sz << f_dwread_epd(_reftable_epd)
        _value << variable
        _result_epd << EPD(variable.getValueAddr())

    def on_init(self):
        _dispmode << DISPMODE_MAIN
        _index << 0
        def func(i, name_epd, value_epd):
            if EUDIf()(MemoryEPD(value_epd, Exactly, _value)):
                _index << i
                EUDReturn()
            EUDEndIf()

        rt.ReferenceTable.iter_table(_reftable_epd, func)

        # failed on search
        _value << f_dwread_epd(_reftable_epd+2)

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
            _focus_index(_index - ENTRY_COUNT_PER_PAGE)
        if EUDElseIf()(app_manager.key_press("F7")):
            _focus_index(_index - 1)
        if EUDElseIf()(app_manager.key_press("F8", hold=["LCTRL"])):
            _focus_index(_index + ENTRY_COUNT_PER_PAGE)
        if EUDElseIf()(app_manager.key_press("F8")):
            _focus_index(_index + 1)
        if EUDElseIf()(app_manager.key_down("F1")):
            _dispmode << DISPMODE_MANUAL
            app_manager.request_update()
        if EUDElseIf()(app_manager.key_up("F1")):
            _dispmode << DISPMODE_MAIN
            app_manager.request_update()
        EUDEndIf()

    def print(self, writer):
        if EUDIf()(_dispmode == DISPMODE_MAIN):
            writer.write_f("\x04SelectorApp, value=%D, press F1\n", _value)
        if EUDElse()():
            writer.write_f(
                "\x17Press F7, F8 to navigate items // "
                "Try combine them with CTRL key. Choose item and press ESC\n"
            )
        EUDEndIf()

        quot, rem = f_div(_index, ENTRY_COUNT_PER_PAGE)
        cur = quot * ENTRY_COUNT_PER_PAGE
        pageend = cur + ENTRY_COUNT_PER_PAGE
        until = EUDVariable()
        text_table_epd = EUDVariable()

        if EUDIf()(pageend <= _reftable_sz):
            until << pageend
        if EUDElse()():
            until << _reftable_sz
        EUDEndIf()

        # print contents
        key_epd = _reftable_epd + 1 + cur * 2
        value_epd = key_epd + 1
        if EUDInfLoop()():
            EUDBreakIf(cur >= until)

            _emp = EUDTernary(cur == _index)(0x11)(0x02)

            if EUDIf()(_dispmode == DISPMODE_MANUAL):
                writer.write_f("\x17 %D:", f_dwread_epd(value_epd))
            EUDEndIf()

            writer.write_f("%C %E\n", _emp, f_dwread_epd(key_epd))

            DoActions([
                cur.AddNumber(1),
                key_epd.AddNumber(2),
                value_epd.AddNumber(2),
            ])
        EUDEndInfLoop()

        # print spaces
        if EUDInfLoop()():
            EUDBreakIf(cur >= pageend)
            writer.write(ord('\n'))
            cur += 1
        EUDEndInfLoop()

        writer.write(0)
