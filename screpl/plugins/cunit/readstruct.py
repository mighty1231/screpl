"""Defines ReadStructApp

TUI:

.. code-block:: text

    ReadStruct - exports CUnit to bridge client
    Mode: selected all

    Press CTRL+O to change mode
    Press CTRL+Y to export
"""
from eudplib import *

from screpl.core.appcommand import AppCommand
from screpl.core.application import Application
from screpl.core.appmethod import AppTypedMethod
from screpl.encoder.const import ArgEncNumber
from screpl.main import get_app_manager, get_main_writer
import screpl.resources.table.tables as tb

STATE_CONFIG = 0
STATE_EXPORTING = 1
v_state = EUDVariable(STATE_CONFIG)

MODE_SELECTED = 0
MODE_ALL = 1
MODE_END = 2
v_mode = EUDVariable(MODE_SELECTED)

storage = Db(170000)
v_remaining_bytes = EUDVariable(0)
v_written = EUDVariable(0)

app_manager = get_app_manager()

@EUDFunc
def get_unit_index_from_addr(addr):
    """Transform CUnit address to index"""
    if EUDIf()(addr == 0x59CCA8):
        EUDReturn(0)
    if EUDElse()():
        EUDReturn((0x6283E8 - addr)//0x150)
    EUDEndIf()

def _write_cunits():
    """Write cunit structures to storage"""
    global v_state, v_mode

    writer = get_main_writer()
    writer.seekepd(EPD(storage))
    writer.write_f("[ReadStruct]\n")

    # format: 0x(ptr) (index): unit type
    if EUDIf()(v_mode == MODE_SELECTED):
        # 0x6284B8
        v_selected_epd = EUDVariable()
        v_selected_epd << EPD(0x6284B8)
        if EUDInfLoop()():
            EUDBreakIf(v_selected_epd >= EPD(0x6284B8 + 12*4))

            v_cunit, v_cunit_epd = f_cunitepdread_epd(v_selected_epd)
            EUDBreakIf(v_cunit == 0)

            writer.write_f("%H %D: ",
                v_cunit,
                get_unit_index_from_addr(v_cunit))
            writer.write_unit(f_wread_epd(v_cunit_epd + (0x64//4), 0))
            writer.write_f("\n")

            v_selected_epd += 1
        EUDEndInfLoop()
    if EUDElse()():
        c_idcheck = Forward()
        v_cunit, v_cunit_epd, v_idx = EUDCreateVariables(3)

        # index 0
        v_cunit << 0x59CCA8
        v_cunit_epd << EPD(0x59CCA8)

        # order check (0 for dead unit)
        if EUDIfNot()(MemoryX(0x59CCA8 + 0x4C, Exactly, 0, 0x0000FF00)):
            writer.write_f("0x0059CCA8 0: ")
            writer.write_constant(EPD(tb.Player),
                                  f_bread_epd(EPD(0x59CCA8 + 0x4C), 0))
            writer.write_f(" ")
            writer.write_unit(f_wread_epd(EPD(0x59CCA8 + 0x64), 0))
            writer.write_f("\n")
        EUDEndIf()

        # prepare loop for 1-1699
        DoActions([
            SetMemory(c_idcheck + 4, SetTo, EPD(0x628298 + 0x4C)),
            v_cunit.SetNumber(0x628298),
            v_cunit_epd.SetNumber(EPD(0x628298)),
            v_idx.SetNumber(1),
        ])
        if EUDInfLoop()():
            EUDBreakIf(v_cunit == 0x59CCA8)

            # order check (0 for dead unit)
            if EUDIfNot()(c_idcheck << MemoryXEPD(0, Exactly, 0, 0x0000FF00)):
                writer.write_f("%H %D: ", v_cunit, v_idx)
                writer.write_constant(EPD(tb.Player),
                                      f_bread_epd(v_cunit_epd + (0x4C//4), 0))
                writer.write_f(" ")
                writer.write_unit(f_wread_epd(v_cunit_epd + (0x64//4), 0))
                writer.write_f("\n")
            EUDEndIf()

            DoActions([
                SetMemory(c_idcheck + 4, Subtract, 0x150//4),
                v_cunit.SubtractNumber(0x150),
                v_cunit_epd.SubtractNumber(0x150//4),
                v_idx.AddNumber(1),
            ])
        EUDEndInfLoop()
    EUDEndIf()
    writer.write(0)

    v_written << 0
    v_remaining_bytes << (writer.getoffset() - storage)

class ReadStructApp(Application):
    def loop(self):
        global v_written, v_remaining_bytes, v_mode

        if EUDIf()(app_manager.key_press("ESC")):
            app_manager.request_destruct()
            EUDReturn()
        EUDEndIf()

        if EUDIf()(v_state == STATE_CONFIG):
            if EUDIf()(app_manager.key_press("Y", hold = ["LCTRL"])):
                v_state << STATE_EXPORTING
                _write_cunits()
            if EUDElseIf()(app_manager.key_press("O", hold = ["LCTRL"])):
                v_mode += 1
                Trigger(
                    conditions=v_mode.Exactly(MODE_END),
                    actions=v_mode.SetNumber(0)
                )
            EUDEndIf()
        if EUDElse()():
            v_new_written = app_manager.send_app_output_to_bridge(
                storage + v_written,
                v_remaining_bytes)

            v_remaining_bytes -= v_new_written
            v_written += v_new_written
            if EUDIf()(v_remaining_bytes == 0):
                v_state << STATE_CONFIG
            EUDEndIf()
        EUDEndIf()
        app_manager.request_update()

    def print(self, writer):
        writer.write_f("\x16ReadStruct - exports CUnit to bridge client\n")

        if EUDIf()(v_state == STATE_CONFIG):
            e_sel, e_all = EUDCreateVariables(2)
            if EUDIf()(v_mode == MODE_SELECTED):
                DoActions([e_sel.SetNumber(0x11), e_all.SetNumber(0x16)])
            if EUDElse()():
                DoActions([e_sel.SetNumber(0x16), e_all.SetNumber(0x11)])
            EUDEndIf()
            writer.write_f("Mode: %Cselected %Call\x16\n"
                           "\n"
                           "Press CTRL+O to change mode\n"
                           "Press CTRL+Y to export\n", e_sel, e_all)
        if EUDElse()():
            writer.write_f("\x13Sent %D bytes / Remaining %D bytes\n\n\n\n",
                v_written,
                v_remaining_bytes
            )
        EUDEndIf()
        writer.write(0)
