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
from screpl.core.application import Application
from screpl.core.appmethod import AppTypedMethod
from screpl.encoder.const import ArgEncNumber
from screpl.main import get_app_manager
from screpl.utils.struct import REPLStruct
from screpl.utils.conststring import EPDConstString

app_manager = get_app_manager()

_cond_epd = EUDVariable(0)

class TrigEntry(REPLStruct):
    fields = [
        "name_epd",
        "offset_epd",
        "offset_rem",
        "size",
    ]

    @staticmethod
    def construct(name, offset, size):
        obj = TrigEntry.initialize_with(
            EPDConstString(name),
            offset // 4,
            offset % 4,
            size,
        )
        return obj

    def write_bytes(self, writer, trig_epd):
        offset_epd = trig_epd + self.offset_epd
        offset_rem = self.offset_rem
        size = self.size

        if EUDIf()(size == 1):
            writer.write_memory_table_epd(offset_epd,
                                          offset_rem, 1)
        if EUDElseIf()(size == 2):
            writer.write_memory_table_epd(offset_epd,
                                          offset_rem, 2)
        if EUDElse()():
            writer.write_memory_table_epd(offset_epd,
                                          0, 4)
        EUDEndIf()

    @EUDMethod
    def set_value(self, trig_epd, value):
        offset_epd = trig_epd + self.offset_epd
        offset_rem = self.offset_rem
        size = self.size

        if EUDIf()(size == 1):
            f_bwrite_epd(offset_epd, offset_rem, value)
        if EUDElseIf()(size == 2):
            f_wwrite_epd(offset_epd, offset_rem, value)
        if EUDElse()():
            f_dwwrite_epd(offset_epd, value)
        EUDEndIf()

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

v_focus = EUDVariable(0)
v_focused_entry = EUDVariable(0)

db_storage = Db(20)

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

        Condition editor on 0x13131312
        SetSwitch("Switch 1", Set)

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

    def on_destruct(self):
        _cond_epd << EPD(0)

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
            f_repmovsd_epd(_cond_epd, EPD(db_storage), 20//4)
            app_manager.request_destruct()
            EUDReturn()
        if EUDElseIf()(app_manager.key_press("F7")):
            set_focus(v_focus - 1)
        if EUDElseIf()(app_manager.key_press("F8")):
            set_focus(v_focus + 1)
        EUDEndIf()
        app_manager.request_update()

    def print(self, writer):
        writer.write_f("\x04Condition on %H\n", 0x58A364 + 4*_cond_epd)
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
        writer.write(0)
