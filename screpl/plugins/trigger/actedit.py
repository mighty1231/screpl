"""TrigActionEditorApp

 ======  ============= ========  ==========
 Offset  Field Name    Position  EPD Player
 ======  ============= ========  ==========
   +00   locid1         dword0   EPD(act)+0
   +04   strid          dword1   EPD(act)+1
   +08   wavid          dword2   EPD(act)+2
   +0C   time           dword3   EPD(act)+3
   +10   player1        dword4   EPD(act)+4
   +14   player2        dword5   EPD(act)+5
   +18   unitid         dword6   EPD(act)+6
   +1A   acttype
   +1B   amount
   +1C   flags          dword7   EPD(act)+7
   +1D   internal0
   +1E   internal1
 ======  ============= ========  ==========
"""
from eudplib import *

from screpl.core.appcommand import AppCommand
from screpl.core.appmethod import AppTypedMethod
from screpl.core.application import Application
from screpl.encoder.const import ArgEncNumber

import screpl.resources.table.tables as tb

from screpl.apps.selector import SelectorApp
from screpl.plugins.location.manager import LocationManagerApp
from screpl.plugins.string.manager import StringManagerApp
from screpl.plugins.switch.manager import SwitchManagerApp
from screpl.plugins.unit.manager import UnitManagerApp

from screpl.main import get_app_manager

from .trigentry import TrigEntry

app_manager = get_app_manager()

entries = [
    # line 1
    TrigEntry.construct("locid1", 0, 4),
    TrigEntry.construct("strid", 0x4, 4),
    TrigEntry.construct("wavid", 0x8, 4),
    TrigEntry.construct("time", 0xC, 4),

    # line 2
    TrigEntry.construct("player1", 0x10, 4),
    TrigEntry.construct("player2", 0x14, 4),
    TrigEntry.construct("unitid", 0x18, 2),
    TrigEntry.construct("acttype", 0x1A, 1),
    TrigEntry.construct("amount", 0x1B, 1),
    TrigEntry.construct("flags", 0x1C, 1),
    TrigEntry.construct("internal1", 0x1D, 1),
    TrigEntry.construct("internal2", 0x1E, 2),
]
entry_cnt = len(entries)
entries = EUDArray(entries)

_act_epd = EUDVariable(0)
v_focus = EUDVariable(0)
v_focused_entry = EUDVariable(0)

db_storage = Db(32)

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

class TrigActionEditorApp(Application):
    """Trigger action editor

    Expected TUI:

    .. code-block:: text

        Action editor on 0x13131312 (Press F1 to get help)
        SetSwitch("Switch 1", Set)

        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
        entry name: amount

        [ Save (CTRL+Y) ] [ CANCEL (CTRL+N) ]
    """
    @staticmethod
    def set_act_epd(act_epd):
        _act_epd << act_epd

    def on_init(self):
        f_repmovsd_epd(EPD(db_storage), _act_epd, 32//4)
        v_focus << 0
        v_focused_entry << entries[0]
        v_mode << MODE_MAIN

    def on_destruct(self):
        _act_epd << EPD(0)

    def on_resume(self):
        self.set_focused_value(v_value_to_set)

    @AppCommand([ArgEncNumber])
    def setn(self, value):
        self.set_focused_value(value)

    @AppCommand([])
    def ActionType(self):
        v_value_to_set << self.get_focused_value()
        SelectorApp.set_content(tb.ActionType, v_value_to_set)
        app_manager.start_application(SelectorApp)

    @AppCommand([])
    def AllyStatus(self):
        v_value_to_set << self.get_focused_value()
        SelectorApp.set_content(tb.AllyStatus, v_value_to_set)
        app_manager.start_application(SelectorApp)

    @AppCommand([])
    def Count(self):
        v_value_to_set << self.get_focused_value()
        SelectorApp.set_content(tb.Count, v_value_to_set)
        app_manager.start_application(SelectorApp)

    @AppCommand([])
    def Modifier(self):
        v_value_to_set << self.get_focused_value()
        SelectorApp.set_content(tb.Modifier, v_value_to_set)
        app_manager.start_application(SelectorApp)

    @AppCommand([])
    def Order(self):
        v_value_to_set << self.get_focused_value()
        SelectorApp.set_content(tb.Order, v_value_to_set)
        app_manager.start_application(SelectorApp)

    @AppCommand([])
    def Player(self):
        v_value_to_set << self.get_focused_value()
        SelectorApp.set_content(tb.Player, v_value_to_set)
        app_manager.start_application(SelectorApp)

    @AppCommand([])
    def Property(self):
        v_value_to_set << self.get_focused_value()
        SelectorApp.set_content(tb.Property, v_value_to_set)
        app_manager.start_application(SelectorApp)

    @AppCommand([])
    def PropState(self):
        v_value_to_set << self.get_focused_value()
        SelectorApp.set_content(tb.PropState, v_value_to_set)
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
    def SwitchAction(self):
        v_value_to_set << self.get_focused_value()
        SelectorApp.set_content(tb.SwitchAction, v_value_to_set)
        app_manager.start_application(SelectorApp)

    @AppCommand([])
    def AIScript(self):
        v_value_to_set << self.get_focused_value()
        SelectorApp.set_content(tb.AIScript, v_value_to_set)
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
    def String(self):
        v_value_to_set << self.get_focused_value()
        StringManagerApp.set_return(v_value_to_set)
        app_manager.start_application(StringManagerApp)

    @AppCommand([])
    def Switch(self):
        v_value_to_set << self.get_focused_value()
        SwitchManagerApp.set_content(v_value_to_set)
        app_manager.start_application(SwitchManagerApp)

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
            f_repmovsd_epd(_act_epd, EPD(db_storage), 32//4)
            app_manager.request_destruct()
            EUDReturn()
        if EUDElseIf()(app_manager.key_press("F7")):
            set_focus(v_focus - 1)
        if EUDElseIf()(app_manager.key_press("F8")):
            set_focus(v_focus + 1)
        if EUDElseIf()(app_manager.key_down("F1")):
            v_mode << MODE_HELP
        if EUDElseIf()(app_manager.key_up("F1")):
            v_mode << MODE_MAIN
        EUDEndIf()
        app_manager.request_update()

    def print(self, writer):
        if EUDIf()(v_mode == MODE_MAIN):
            writer.write_f("\x04Action on %H (Press F1 to get help)\n",
                           0x58A364 + 4*_act_epd)
            writer.write_action_epd(EPD(db_storage))
            writer.write_f("\n\n")

            i = EUDVariable()
            i << 0
            if EUDWhileNot()(i >= entry_cnt):
                entry = TrigEntry.cast(entries[i])
                color = EUDTernary(i == v_focus)(0x11)(0x2)

                # seperate line
                if EUDIf()(i == 4):
                    writer.write(ord('\n'))
                EUDEndIf()

                writer.write(color)
                entry.write_bytes(writer, EPD(db_storage))
                i += 1
            EUDEndWhile()

            writer.write_f("\n\x04entry: \x11%E\n"
                           "\n"
                           "\x04[ Save (CTRL+Y) ] [ CANCEL (CTRL+N) ]\n",
                           TrigEntry.cast(v_focused_entry).name_epd)
        if EUDElse()():
            writer.write_f(
                "\x04Action Editor App\n"
                "Press F7, F8 to change focus\n"
                "Chat 'setn(##)' to set the value of focused entry\n"
                "Chat followings to set value with helper apps\n"
                "  ActionType(), AllyStatus(), Count(), Modifier(), Order(), "
                "Player(), Property(), PropState(), Resource(), Score()\n"
                "  SwitchAction(), AIScript(), Location(), String(), Switch()"
                "Unit()\n")
        EUDEndIf()
        writer.write(0)
