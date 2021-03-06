"""Defines CondCheckApp"""
from eudplib import *

from screpl.core.application import Application
from screpl.main import get_app_manager
from screpl.main import get_main_writer
from screpl.resources.table.tables import Player, ConditionType

from . import cctm
from .entry import MaximumCircularBuffer, ResultEntry
from .editor import TriggerEditorApp

app_manager = get_app_manager()
writer = get_main_writer()

arr_trig_object = []
arr_trigid = []
arr_pid = []
arr_mcb = []
for _trig_object, _trigid, _pid, _mcb in cctm.result_tables:
    arr_trig_object.append(_trig_object)
    arr_trigid.append(_trigid)
    arr_pid.append(_pid)
    arr_mcb.append(_mcb)

arr_length = len(cctm.result_tables)
arr_trig_object = EUDArray(arr_trig_object)
arr_trigid = EUDArray(arr_trigid)
arr_pid = EUDArray(arr_pid)
arr_mcb = EUDArray(arr_mcb)

v_focus = EUDVariable(0)

MODE_MAIN = 0
MODE_HELP = 1
v_mode = EUDVariable(0)

@EUDTypedFunc([ResultEntry])
def write_entry(entry):
    start_tick = entry.start_tick
    end_tick = entry.end_tick
    cond_count = entry.cond_count
    cond_bools_epd = entry.cond_bools_epd
    cond_values_epd = entry.cond_values_epd
    cond_types_epd = entry.cond_types_epd

    writer.write_f("\x16%D-%D: ", start_tick, end_tick)
    if EUDWhileNot()(cond_count == 0):
        writer.write(EUDTernary(MemoryEPD(cond_bools_epd, Exactly, 0))(6)(7))
        if EUDIfNot()(MemoryEPD(cond_types_epd, Exactly, 0)):
            writer.write_constant(EPD(ConditionType),
                                  f_dwread_epd(cond_types_epd))
            writer.write(ord(':'))
        EUDEndIf()
        writer.write_f("%D ", f_dwread_epd(cond_values_epd))

        DoActions([
            cond_count.SubtractNumber(1),
            cond_bools_epd.AddNumber(1),
            cond_values_epd.AddNumber(1),
            cond_types_epd.AddNumber(1),
        ])
    EUDEndWhile()
    writer.write_f("\n")

def _set_focus(new_focus):
    global v_focus
    if EUDIfNot()(new_focus >= arr_length):
        v_focus << new_focus
    EUDEndIf()

class CondCheckApp(Application):
    def on_init(self):
        v_mode << MODE_MAIN

    def loop(self):
        if EUDIf()(app_manager.key_press("ESC")):
            app_manager.request_destruct()
        if EUDElseIf()(app_manager.key_press("F7")):
            _set_focus(v_focus-1)
        if EUDElseIf()(app_manager.key_press("F8")):
            _set_focus(v_focus+1)
        if EUDElseIf()(app_manager.key_down("F1")):
            v_mode << MODE_HELP
        if EUDElseIf()(app_manager.key_up("F1")):
            v_mode << MODE_MAIN
        if EUDElseIf()(app_manager.key_press("E", hold=["LCTRL"])):
            TriggerEditorApp.set_trig_ptr(arr_trig_object[v_focus], nolink=True)
            app_manager.start_application(TriggerEditorApp)
        EUDEndIf()
        app_manager.request_update()

    def print(self, writer):
        if EUDIf()(v_mode == MODE_MAIN):
            trigid = arr_trigid[v_focus]
            pid = arr_pid[v_focus]
            mcb = MaximumCircularBuffer(ResultEntry).cast(arr_mcb[v_focus])

            writer.write_f("\x04Condition check [%D/%D] - Trigger[%D] player=",
                           v_focus + 1, arr_length, trigid)
            writer.write_constant(EPD(Player), pid)
            writer.write_f(", press F1 to help\n")
            mcb.iter(write_entry)
        if EUDElse()():
            writer.write_f(
                "\x04Condition check debugs trigger, logging conditions\n"
                "Navigation: F7/F8, Open trigger manager: CTRL+E\n"
                "Format: \x17(start_tick)-(end_tick): \x0Fv0 v1 v2 ...\n"
                "\x17 - tick\x04: the value of 0x57F23C (f_getgametick())\n"
                "\x04   During \x17start_tick \x04to \x17end_tick\x04, "
                    "all the conditions behaved as the same way\n"
                "\x0F - color of v\x04: condition check result. "
                    "\x07pass \x06fail\n"
                "\x0F - value of v\x04: The exact amount to satisfy "
                    "the \x1Fcomparison conditions\n"
            )
        EUDEndIf()
        writer.write(0)
