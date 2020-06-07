from eudplib import *

from screpl.core.application import Application
from screpl.resources.table.tables import get_switchname_epd
from screpl.main import get_app_manager

ENTRY_COUNT_PER_PAGE = 8

app_manager = get_app_manager()

_index = EUDVariable()
_result_epd = EUDVariable(EPD(0))

@EUDFunc
def _focus_index(new_index):
    Trigger(
        conditions=new_index.AtLeast(0x80000000),
        actions=new_index.SetNumber(0)
    )
    Trigger(
        conditions=new_index.AtLeast(256),
        actions=new_index.SetNumber(255)
    )
    if EUDIfNot()(new_index == _index):
        _index << new_index
        app_manager.request_update()
    EUDEndIf()

class SwitchManagerApp(Application):
    @staticmethod
    def set_content(variable):
        assert IsEUDVariable(variable)

        _index << variable
        _result_epd << EPD(variable.getValueAddr())

    def on_init(self):
        if EUDIf()(_index >= 256):
            _index << 0
        EUDEndIf()

    def on_destruct(self):
        if EUDIfNot()(_result_epd == EPD(0)):
            f_dwwrite_epd(_result_epd, _index)
        EUDEndIf()
        _result_epd << EPD(0)

    def loop(self):
        if EUDIf()(app_manager.key_press("ESC")):
            app_manager.request_destruct()
            EUDReturn()
        if EUDElseIf()(app_manager.key_press("F7", hold=["LCTRL"])):
            _focus_index(_index - 8)
        if EUDElseIf()(app_manager.key_press("F7")):
            _focus_index(_index - 1)
        if EUDElseIf()(app_manager.key_press("F8", hold=["LCTRL"])):
            _focus_index(_index + 8)
        if EUDElseIf()(app_manager.key_press("F8")):
            _focus_index(_index + 1)
        EUDEndIf()

    def print(self, writer):
        writer.write_f("\x16Switch Manager\n")

        quot, rem = f_div(_index, ENTRY_COUNT_PER_PAGE)
        cur = quot * ENTRY_COUNT_PER_PAGE
        pageend = cur + ENTRY_COUNT_PER_PAGE
        until = EUDVariable()

        if EUDIf()(pageend <= 256):
            until << pageend
        if EUDElse()():
            until << 256
        EUDEndIf()

        # print contents
        if EUDInfLoop()():
            EUDBreakIf(cur >= until)

            _emp = EUDTernary(cur == _index)(0x11)(0x02)

            writer.write_f("%C %D: %E", _emp, cur, get_switchname_epd(cur))

            if EUDIf()(Switch(cur, Set)):
                writer.write_f("\x07Set\n")
            if EUDElse()():
                writer.write_f("\x06Cleared\n")
            EUDEndIf()

            DoActions(cur.AddNumber(1))
        EUDEndInfLoop()

        # print spaces
        if EUDInfLoop()():
            EUDBreakIf(cur >= pageend)
            writer.write(ord('\n'))
            cur += 1
        EUDEndInfLoop()

        writer.write(0)
