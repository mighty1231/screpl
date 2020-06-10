'''
feature
 * delete
 * modify
 * new
Expected TUI
 1. Pattern {pattern_id} actions, ESC to back
 2.  1. Create..
 3.  2. Kill..
 4.  3. ...
'''
from eudplib import *

from screpl.core.application import Application
from screpl.plugins.location.rect import draw_rectangle
from screpl.plugins.trigger.actedit import TrigActionEditorApp

from . import (
    app_manager,
    focused_pattern_id,
    p_action_count,
    p_action_array_epd,
)

action_id = EUDVariable(0)
action_count = EUDVariable(0)
action_array_epd = EUDVariable(0)
frame = EUDVariable(0)

FRAME_PERIOD = 24

@EUDFunc
def focus_action_id(new_actionid):
    if EUDIfNot()(new_actionid >= action_count):
        if EUDIfNot()(new_actionid == action_id):
            action_id << new_actionid
            app_manager.request_update()
        EUDEndIf()
    EUDEndIf()

def delete_action():
    global action_id
    if EUDIfNot()(action_count == 0):
        cur_action_epd = action_array_epd + (32//4) * action_id
        next_action_epd = cur_action_epd + (32//4)
        _until_epd = action_array_epd + (32//4) * action_count

        # overwrite
        if EUDInfLoop()():
            EUDBreakIf(next_action_epd == _until_epd)

            f_repmovsd_epd(cur_action_epd, next_action_epd, 32//4)

            DoActions([
                cur_action_epd.AddNumber(32//4),
                next_action_epd.AddNumber(32//4)
            ])
        EUDEndInfLoop()

        DoActions([
            action_count.SubtractNumber(1),
            SetMemoryEPD(EPD(p_action_count) + focused_pattern_id, Subtract, 1)
        ])

        if EUDIf()(action_id == action_count):
            action_id -= 1
        EUDEndIf()
        app_manager.request_update()
    EUDEndIf()


class DetailedActionApp(Application):
    def on_init(self):
        action_count << p_action_count[focused_pattern_id]
        action_id << action_count - 1
        action_array_epd << p_action_array_epd[focused_pattern_id]

    def loop(self):
        if EUDIf()(app_manager.key_press('ESC')):
            app_manager.request_destruct()
            EUDReturn()
        if EUDElseIf()(app_manager.key_press('f7')):
            focus_action_id(action_id-1)
        if EUDElseIf()(app_manager.key_press('f8')):
            focus_action_id(action_id+1)
        if EUDElseIf()(app_manager.key_press('delete')):
            delete_action()
        if EUDElseIf()(app_manager.key_press('E', hold=['LCTRL'])):
            TrigActionEditorApp.set_act_epd(
                action_array_epd + (32//4)*action_id)
            app_manager.start_application(TrigActionEditorApp)
        EUDEndIf()

        if EUDIfNot()(action_id == -1):
            action_epd = action_array_epd + (32//4) * action_id

            locid1 = f_dwread_epd(action_epd)
            if EUDIfNot()(locid1 == 0):
                draw_rectangle(locid1, frame, FRAME_PERIOD)
            EUDEndIf()

            # graphical set
            DoActions(frame.AddNumber(1))
            if EUDIf()(frame == FRAME_PERIOD):
                DoActions(frame.SetNumber(0))
            EUDEndIf()
        EUDEndIf()

    def print(self, writer):
        writer.write_f("Pattern %D action editor, "\
                "press 'ESC' to go back (F7, F8, Delete)\n", focused_pattern_id+1)

        if EUDIf()(action_id == -1):
            writer.write(0)
            EUDReturn()
        EUDEndIf()

        quot = f_div(action_id, 8)[0]
        cur = quot * 8
        pageend = cur + 8
        until = EUDVariable()
        if EUDIf()(pageend <= action_count):
            until << pageend
        if EUDElse()():
            until << action_count
        EUDEndIf()

        # fill contents
        action_epd = action_array_epd + (32//4) * cur
        if EUDInfLoop()():
            EUDBreakIf(cur >= until)

            if EUDIf()(cur == action_id):
                writer.write(0x11) # orange
            if EUDElse()():
                writer.write(0x02) # pale blue
            EUDEndIf()

            writer.write_f(" %D: ", cur)
            writer.write_action_epd(action_epd)
            writer.write(ord('\n'))

            DoActions([cur.AddNumber(1), action_epd.AddNumber(32//4)])
        EUDEndInfLoop()

        writer.write(0)
