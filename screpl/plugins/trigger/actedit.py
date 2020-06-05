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
from screpl.core.application import Application
from screpl.encoder.const import ArgEncNumber
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

        Action editor on 0x13131312
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

    def on_destruct(self):
        _act_epd << EPD(0)

    @AppCommand([ArgEncNumber])
    def setn(self, value):
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
        EUDEndIf()
        app_manager.request_update()

    def print(self, writer):
        writer.write_f("\x04Action on %H\n", 0x58A364 + 4*_act_epd)
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
        writer.write(0)
