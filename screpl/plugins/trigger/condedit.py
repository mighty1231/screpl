"""TrigConditionEditorApp

 ======  =============  ========  ===========
 Offset  Field name     Position  EPD Player
 ======  =============  ========  ===========
   +00   locid           dword0   EPD(cond)+0
   +04   player          dword1   EPD(cond)+1
   +08   amount          dword2   EPD(cond)+2
   +0C   unitid          dword3   EPD(cond)+3
   +0E   comparison
   +0F   condtype
   +10   restype         dword4   EPD(cond)+4
   +11   flags
   +12   internal[2]
 ======  =============  ========  ===========
"""
from eudplib import *

from screpl.core.appcommand import AppCommand
from screpl.core.appmethod import AppTypedMethod
from screpl.core.application import Application
from screpl.encoder.const import ArgEncNumber

import screpl.resources.table.tables as tb

from screpl.apps.selector import SelectorApp
from screpl.plugins.unit.manager import UnitManagerApp
from screpl.plugins.location.manager import LocationManagerApp

from screpl.main import get_app_manager

from .trigentry import TrigEntry

app_manager = get_app_manager()

entries = [
    TrigEntry.construct("locid", 0, 4),
    TrigEntry.construct("player", 0x4, 4),
    TrigEntry.construct("amount", 0x8, 4),
    TrigEntry.construct("unitid", 0xC, 2),
    TrigEntry.construct("comparison", 0xE, 1),
    TrigEntry.construct("condtype", 0xF, 1),
    TrigEntry.construct("restype", 0x10, 1),
    TrigEntry.construct("flags", 0x11, 1),
    TrigEntry.construct("internal", 0x12, 2),
]
entry_cnt = len(entries)
entries = EUDArray(entries)

_cond_epd = EUDVariable(0)
v_focus = EUDVariable(0)
v_focused_entry = EUDVariable(0)

db_storage = Db(20)

MODE_MAIN = 0
MODE_HELP = 1
v_mode = EUDVariable(MODE_MAIN)

# call value selector apps, and get value from them
v_value_to_set = EUDVariable()

@EUDFunc
def set_focus(new_focus):
    if EUDIfNot()(new_focus >= entry_cnt):
        v_focus << new_focus
        v_focused_entry << entries[v_focus]
        app_manager.request_update()
    EUDEndIf()

class TrigConditionEditorApp(Application):
    """Trigger condition editor

    Expected TUI:

    .. code-block:: text

        Condition editor on 0x13131312 (Press F1 to get help)
        Switch("Switch 1", Set)

        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
        entry name: amount

        [ Save (CTRL+Y) ] [ CANCEL (CTRL+N) ]
    """
    @staticmethod
    def set_cond_epd(cond_epd):
        _cond_epd << cond_epd

    def on_init(self):
        f_repmovsd_epd(EPD(db_storage), _cond_epd, 20//4)
        v_focus << 0
        v_focused_entry << entries[0]
        v_mode << MODE_MAIN

    def on_destruct(self):
        _cond_epd << EPD(0)

    def on_resume(self):
        self.set_focused_value(v_value_to_set)

    @AppCommand([ArgEncNumber])
    def setn(self, value):
        self.set_focused_value(value)

    @AppCommand([])
    def ConditionType(self):
        pass

    @AppCommand([])
    def Comparison(self):
        v_value_to_set << self.get_focused_value()
        SelectorApp.set_content(tb.Comparison, v_value_to_set)
        app_manager.start_application(SelectorApp)

    @AppCommand([])
    def Player(self):
        v_value_to_set << self.get_focused_value()
        SelectorApp.set_content(tb.Player, v_value_to_set)
        app_manager.start_application(SelectorApp)

    @AppCommand([])
    def Resource(self):
        v_value_to_set << self.get_focused_value()
        SelectorApp.set_content(tb.Resource, v_value_to_set)
        app_manager.start_application(SelectorApp)

    @AppCommand([])
    def Score(self):
        v_value_to_set << self.get_focused_value()
        SelectorApp.set_content(tb.Score, v_value_to_set)
        app_manager.start_application(SelectorApp)

    @AppCommand([])
    def SwitchState(self):
        v_value_to_set << self.get_focused_value()
        SelectorApp.set_content(tb.SwitchState, v_value_to_set)
        app_manager.start_application(SelectorApp)

    @AppCommand([])
    def Location(self):
        v_value_to_set << self.get_focused_value()
        LocationManagerApp.set_content(
            v_value_to_set,
            EPD(v_value_to_set.getValueAddr()),
        )
        app_manager.start_application(LocationManagerApp)

    @AppCommand([])
    def Switch(self):
        pass

    @AppCommand([])
    def Unit(self):
        v_value_to_set << self.get_focused_value()
        UnitManagerApp.set_content(
            v_value_to_set,
            EPD(v_value_to_set.getValueAddr()),
        )
        app_manager.start_application(UnitManagerApp)

    @AppTypedMethod([], [None])
    def get_focused_value(self):
        focused_entry = TrigEntry.cast(v_focused_entry)
        EUDReturn(focused_entry.get_value(EPD(db_storage)))

    def set_focused_value(self, value):
        focused_entry = TrigEntry.cast(v_focused_entry)
        focused_entry.set_value(EPD(db_storage), value)

    def loop(self):
        if EUDIf()(app_manager.key_press("ESC")):
            app_manager.request_destruct()
            EUDReturn()
        if EUDElseIf()(app_manager.key_press("N", hold=["LCTRL"])):
            app_manager.request_destruct()
            EUDReturn()
        if EUDElseIf()(app_manager.key_press("Y", hold=["LCTRL"])):
            f_repmovsd_epd(_cond_epd, EPD(db_storage), 20//4)
            app_manager.request_destruct()
            EUDReturn()
        if EUDElseIf()(app_manager.key_press("F7")):
            set_focus(v_focus - 1)
        if EUDElseIf()(app_manager.key_press("F8")):
            set_focus(v_focus + 1)
        if EUDElseIf()(app_manager.key_down("F1")):
            v_mode << MODE_HELP
            app_manager.clean_text()
        if EUDElseIf()(app_manager.key_up("F1")):
            v_mode << MODE_MAIN
            app_manager.clean_text()
        EUDEndIf()
        app_manager.request_update()

    def print(self, writer):
        if EUDIf()(v_mode == MODE_MAIN):
            writer.write_f("\x04Condition on %H (Press F1 to get help)\n",
                           0x58A364 + 4*_cond_epd)
            writer.write_condition_epd(EPD(db_storage))
            writer.write_f("\n\n")

            i = EUDVariable()
            i << 0
            if EUDWhileNot()(i >= entry_cnt):
                entry = TrigEntry.cast(entries[i])
                color = EUDTernary(i == v_focus)(0x11)(0x2)

                writer.write(color)
                entry.write_bytes(writer, EPD(db_storage))
                i += 1
            EUDEndWhile()

            writer.write_f("\n\x04entry: \x11%E\n"
                           "\n"
                           "\x04[ Save (CTRL+Y) ] [ CANCEL (CTRL+N) ]\n",
                           TrigEntry.cast(v_focused_entry).name_epd)
        if EUDElse()():
            writer.write_f("\x04Condition Editor App\n"
                           "Press F7, F8 to change focus\n"
                           "Chat 'setn(##)' sets the value of focused entry\n"
                           "For example,\n"
                           "\x041. \x02%Ssetn(33)\n"
                           "\x042. \x02%Ssetn(0xFFFFFFFF)\n",
                           app_manager.su_prefix, app_manager.su_prefix)
        EUDEndIf()
        writer.write(0)
