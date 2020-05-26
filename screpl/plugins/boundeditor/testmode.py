""" TestPatternApp

Expected TUI

.. code-block:: text

     1. Bound Editor - TEST MODE
     2. Timer = {timer}
     3.
     4.
     5. Press 'R' to reset
     6. Start location: {g_start_location}
     7.
     8.
     9.
    10.
    11.
"""
from eudplib import *

from screpl.core.application import Application
from screpl.writer import write_location

from . import (
    app_manager,
    su_id,
    g_runner_unit,
    g_start_location,
    executePattern,
    p_waitValue,
    p_count
)

timer = EUDVariable(0)
pattern_id = EUDVariable(0)
next_timer = EUDVariable(0)
last_tick = EUDVariable(0)
cur_tick = EUDVariable()

TURBOMODE_EUDTURBO = 0
TURBOMODE_TURBO    = 1
TURBOMODE_NOTURBO  = 2
TURBOMODE_END      = 3
v_turbomode = EUDVariable(TURBOMODE_NOTURBO)

class TestPatternApp(Application):
    def on_init(self):
        timer << 0
        pattern_id << 0
        next_timer << 0
        cur_tick << f_getgametick()

    def loop(self):
        global timer, pattern_id, next_timer, v_turbomode
        if EUDIf()(app_manager.key_press('ESC')):
            app_manager.request_destruct()
            EUDReturn()
        if EUDElseIf()(app_manager.key_press('R')):
            DoActions([
                timer.SetNumber(0),
                pattern_id.SetNumber(0),
                next_timer.SetNumber(0),
            ])
        if EUDElseIf()(app_manager.key_press('T')):
            v_turbomode += 1
            Trigger(
                conditions = [v_turbomode.Exactly(TURBOMODE_END)],
                actions = [v_turbomode.SetNumber(0)]
            )
        EUDEndIf()

        # Create Tester Unit for every death
        Trigger(
            conditions = [Bring(su_id, Exactly, 0, g_runner_unit, g_start_location)],
            actions = [CreateUnit(1, g_runner_unit, g_start_location, su_id)]
        )

        # Timer
        if EUDIf()(timer == next_timer):
            executePattern(pattern_id)

            # timer reset
            if EUDIf()(pattern_id == 0):
                timer << 0
                next_timer << 0
            EUDEndIf()

            # set next timer
            next_timer += p_waitValue[pattern_id]
            pattern_id += 1
            if EUDIf()(pattern_id == p_count):
                pattern_id << 0
            EUDEndIf()
        EUDEndIf()
        DoActions(timer.AddNumber(1))

        # observe frame count
        last_tick << cur_tick
        cur_tick << f_getgametick()

        if EUDIf()(v_turbomode == TURBOMODE_EUDTURBO):
            DoActions([SetMemory(0x6509A0, SetTo, 0)])
        if EUDElseIf()(v_turbomode == TURBOMODE_TURBO):
            DoActions([SetMemory(0x6509A0, SetTo, 1)])
        EUDEndIf()

        app_manager.request_update()

    def print(self, writer):
        writer.write_f("Bound Editor Test Mode\n")
        writer.write_f("Press 'R' to reset, press 'ESC' to end test\n")
        writer.write_f("Timer = %D\n\n", timer)

        obs_trig_delay = cur_tick - last_tick
        writer.write_f("Observed trigger delay = %D " \
                "(1:eudturbo, 2:turbo, 31:noturbo)\n", obs_trig_delay)

        writer.write_f("Set trigger delay mode (T): ", )
        if EUDIf()(v_turbomode == TURBOMODE_EUDTURBO):
            writer.write_f("eudturbo")
            if EUDIfNot()(obs_trig_delay == 1):
                writer.write_f(" \x06Mismatch on delay: \x03wait trigger on somewhere?")
            EUDEndIf()
        if EUDElseIf()(v_turbomode == TURBOMODE_TURBO):
            writer.write_f("turbo")
            if EUDIfNot()(obs_trig_delay == 2):
                writer.write_f(" \x06Mismatch on delay: \x03eudturbo trigger on somewhere?")
            EUDEndIf()
        if EUDElseIf()(v_turbomode == TURBOMODE_NOTURBO):
            writer.write_f("no turbo")
        EUDEndIf()

        writer.write_f("\n\n\x02Start location: ")
        write_location(g_start_location)
        writer.write(ord('\n'))
        writer.write(0)
