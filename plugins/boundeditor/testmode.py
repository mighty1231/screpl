''' TEST MODE
Expected TUI
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
'''
from eudplib import *

from repl import Application, writeLocation
from . import (
    appManager,
    superuser,
    g_runner_unit,
    g_start_location,
    executePattern,
    p_waitValue,
    p_count
)

timer = EUDVariable(0)
pattern_id = EUDVariable(0)
next_timer = EUDVariable(0)

class TestPatternApp(Application):
    def onInit(self):
        timer << 0
        pattern_id << 0
        next_timer << 0

    def loop(self):
        global timer, pattern_id, next_timer
        if EUDIf()(appManager.keyPress('ESC')):
            appManager.requestDestruct()
            EUDReturn()
        if EUDElseIf()(appManager.keyPress('R')):
            DoActions([
                timer.SetNumber(0),
                pattern_id.SetNumber(0),
                next_timer.SetNumber(0),
            ])
        EUDEndIf()

        # Create Tester Unit for every death
        Trigger(
            conditions = [Bring(superuser, Exactly, 0, g_runner_unit, g_start_location)],
            actions = [CreateUnit(1, g_runner_unit, g_start_location, superuser)]
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

    def print(self, writer):
        writer.write_f("Bound Editor Test Mode\n")
        writer.write_f("Press 'R' to reset, press 'ESC' to end test\n")
        writer.write_f("Timer = %D\n\n", timer)
        writer.write_f("Start location: ")
        writeLocation(g_start_location)
        writer.write(ord('\n'))
        writer.write(0)
