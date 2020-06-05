"""Defines CondCheckApp"""
from eudplib import *

from screpl.core.application import Application
from screpl.main import get_app_manager
from screpl.main import get_main_writer

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

    writer.write_f("\x16%D-%D: ", start_tick, end_tick)
    if EUDWhileNot()(cond_count == 0):
        color = EUDTernary(MemoryEPD(cond_bools_epd, Exactly, 0))(6)(7)
        writer.write_f("%C%D ", color, f_dwread_epd(cond_values_epd))

        DoActions([
            cond_count.SubtractNumber(1),
            cond_bools_epd.AddNumber(1),
            cond_values_epd.AddNumber(1),
        ])
    EUDEndWhile()
    writer.write_f("\n")

def _set_focus(new_focus):
    global v_focus
    if EUDIfNot()(new_focus >= arr_length):
        v_focus << new_focus
        app_manager.clean_text()
    EUDEndIf()

class CondCheckApp(Application):
    def loop(self):
        if EUDIf()(app_manager.key_press("ESC")):
            app_manager.request_destruct()
            EUDReturn()
        if EUDElseIf()(app_manager.key_press("F7")):
            _set_focus(v_focus-1)
        if EUDElseIf()(app_manager.key_press("F8")):
            _set_focus(v_focus+1)
        if EUDElseIf()(app_manager.key_down("H")):
            v_mode << MODE_HELP
            app_manager.clean_text()
        if EUDElseIf()(app_manager.key_up("H")):
            v_mode << MODE_MAIN
            app_manager.clean_text()
        if EUDElseIf()(app_manager.key_press("E", hold=["LCTRL"])):
            TriggerEditorApp.set_trig_ptr(arr_trig_object[v_focus], unlink=True)
            app_manager.start_application(TriggerEditorApp)
        EUDEndIf()
        app_manager.request_update()

    def print(self, writer):
        if EUDIf()(v_mode == MODE_MAIN):
            trigid = arr_trigid[v_focus]
            pid = arr_pid[v_focus]
            mcb = MaximumCircularBuffer(ResultEntry).cast(arr_mcb[v_focus])

            writer.write_f("\x04Condition log - trigid=%D playerid=%D, "
                           "press H to help\n", trigid, pid)
            mcb.iter(write_entry)
        if EUDElse()():
            writer.write_f(
                "\x04Condition log - (Navigation: F7/F8, Trigger: CTRL+E)\n"
                "\x17(start_tick)-(end_tick): \x0Fv0 v1 v2 ...\n"
                "\x17tick\x04: the value of 0x57F23C (f_getgametick())\n"
                "\x04During \x17start_tick \x04to \x17end_tick\x04, "
                    "the condition behaves as all the same way\n"
                "\x0Fcolor of v\x04: condition check result. "
                    "\x07pass \x06fail\n"
                "\x0Fvalue of v\x04: The exact amount to satisfy "
                    "the \x15comparison conditions\n"
                "\n"
                "\x15[Comparison conditions]\n"
                "\x02CountdownTimer, Command, Bring, Accumulate, "
                "Kills, ElapsedTime, Opponents, Deaths, Score\n"
            )
        EUDEndIf()
        writer.write(0)
