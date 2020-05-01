'''
 1. BoundEditor Options
 2. Effect player: P8
 3. Effect unit 1/2/3: Zerg Scourge, Zerg Overlord, Terran Battlecruiser
 4. Obstacle unit: Psi Emitter
 5. Runner force: Force1
 6. Runner unit: Zerg Zergling
 7. Start location: location
 8. Turbo mode: EUDTurbo
 9.
10.
11.
'''

from eudplib import *
from repl import (
    Application,
    AppTypedMethod,
    AppCommand,
    argEncNumber
)

from . import (
    appManager,
    g_effectplayer,
    g_effectunit_1,
    g_effectunit_2,
    g_effectunit_3,
    g_obstacle_unit,
    g_start_location,
    g_runnerforce,
    g_runnerunit,
    g_turbo_mode
)

FOCUS_EFFECTPLAYER = 0
FOCUS_EFFECTUNIT1 = 1
FOCUS_EFFECTUNIT2 = 2
FOCUS_EFFECTUNIT3 = 3
FOCUS_OBSTACLEUNIT = 4
FOCUS_RUNNER_FORCE = 5
FOCUS_RUNNER_UNIT = 6
FOCUS_START_LOCATION = 7
FOCUS_TURBO_MODE = 8
FOCUS_END = 9

focus_modes = [
    FOCUS_EFFECTPLAYER,
    FOCUS_EFFECTUNIT1,
    FOCUS_EFFECTUNIT2,
    FOCUS_EFFECTUNIT3,
    FOCUS_OBSTACLEUNIT,
    FOCUS_RUNNER_FORCE,
    FOCUS_RUNNER_UNIT,
    FOCUS_START_LOCATION,
    FOCUS_TURBO_MODE,
]

focus = EUDVariable(0)

class OptionApp(Application):
    def loop(self):
        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
        if EUDElseIf()(appManager.keyPress("F7")):
            Trigger(
                conditions = focus.Exactly(0),
                actions = focus.SetNumber(FOCUS_END)
            )
            DoActions(focus.SubtractNumber(1))
        if EUDElseIf()(appManager.keyPress("F8")):
            DoActions(focus.AddNumber(1))
            Trigger(
                conditions = focus.Exactly(FOCUS_END),
                actions = focus.SetNumber(0)
            )
        EUDEndIf()
        appManager.requestUpdate()

    def print(self, writer):
        writer.write_f("BoundEditor Options\n")
        writer.write_f("Effect player: P8\n")
        writer.write_f("Effect unit 1/2/3: ")
        writer.write_f("Zerg Scourge, Zerg Overlord, Terran Battlecruiser\n")

        writer.write_f("Obstacle unit: Psi Emitter\n")
        writer.write_f("Runner force: Force1\n")
        writer.write_f("Runner unit: Zerg Zergling\n")
        writer.write_f("Start location: location\n")
        writer.write_f("Turbo mode: EUDTurbo\n")
        write.write(0)
