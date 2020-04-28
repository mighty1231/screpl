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

from repl import Application
from . import appManager, superuser

timer = EUDVariable(0)
pattern_id = EUDVariable(0)
next_timer = EUDVariable(0)

def executeActions(cnt, action_epd):
    i = EUDVariable(0)
    i << 0
    if EUDInfLoop()():
        EUDBreakIf(i >= cnt)

        _nxttrig = Forward()

        # fill trigger
        DoActions(SetNextPtr(emptyTrigger, _nxttrig))
        f_repmovsd_epd(EPD(emptyTrigger + 8 + 320), action_epd, 32 // 4)

        # jump to trigger
        EUDJump(emptyTrigger)
        _nxttrig << NextTrigger()
        DoActions([
            i.AddNumber(1),
            action_epd.AddNumber(32 // 4)
        ])
    EUDEndInfLoop()

class TestPatternApp(Application):
    def onInit(self):
        timer << 0
        pattern_id << 0
        next_timer << 0

    def loop(self):
        if EUDIf()(appManager.keyPress('ESC')):
            appManager.requestDestruct()
        if EUDElseIf()(appManager.keyPress('R')):
            DoActions([
                timer.SetNumber(0),
                pattern_id.SetNumber(0),
                next_timer.SetNumber(0),
                RemoveUnit()
            ])
        EUDEndIf()

        if EUDIf()(p_count == 0):
            f_raiseWarning("Please make your pattern")
            EUDReturn()
        EUDEndIf()

        # Create Tester Unit for every death
        Trigger(
            conditions = [Bring(superuser, Exactly, 0, g_runnerunit, g_start_location)],
            actions = [CreateUnit(1, g_runnerunit, g_start_location, superuser)]
        )

        # Timer
        if EUDIf()(timer == next_timer):
            executeActions(p_actionCount[pattern_id], p_actionArrayEPD[pattern_id])

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

        # turbo mode
        lets_turbo()

    def print(self, writer):
        writer.write_f("Bound Editor - TEST MODE\n")
        writer.write_f("Timer = %D\n\n", timer)
        writer.write_f("Press 'R' to reset, press 'ESC' to end test\n")
        writer.write_f("Start location: %D\n", g_start_location)
