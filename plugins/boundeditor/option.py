'''
 1. BoundEditor Options
 2. Effect player: P8
 3. Effect unit 1/2/3: Zerg Scourge, Zerg Overlord, Terran Battlecruiser
 4. Obstacle unit: Psi Emitter
 5. Runner force: Force1
 6. Runner unit: Zerg Zergling
 7. Start location: location
 8.
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
    g_obstacleunit,
    g_start_location,
    g_runnerforce,
    g_runnerunit
)

FOCUS_EFFECTPLAYER = 0
FOCUS_EFFECTUNIT1 = 1
FOCUS_EFFECTUNIT2 = 2
FOCUS_EFFECTUNIT3 = 3
FOCUS_OBSTACLEUNIT = 4
FOCUS_RUNNER_FORCE = 5
FOCUS_RUNNER_UNIT = 6
FOCUS_START_LOCATION = 7
FOCUS_END = 8

focus_modes = [
    FOCUS_EFFECTPLAYER,
    FOCUS_EFFECTUNIT1,
    FOCUS_EFFECTUNIT2,
    FOCUS_EFFECTUNIT3,
    FOCUS_OBSTACLEUNIT,
    FOCUS_RUNNER_FORCE,
    FOCUS_RUNNER_UNIT,
    FOCUS_START_LOCATION,
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
        if EUDElseIf()(appManager.keyPress("insert")):
            if EUDIf()(focus.Exactly(FOCUS_EFFECTPLAYER)):
                PlayerSelectorApp.setContent(g_effectplayer, EPD(g_effectplayer.getValueAddr()))
                appManager.startApplication(PlayerSelectorApp)
            if EUDElseIf()(focus.Exactly(FOCUS_EFFECTUNIT1)):
                UnitManagerApp.setContent(g_effectunit_1, EPD(g_effectunit_1.getValueAddr()))
                appManager.startApplication(UnitManagerApp)
            if EUDElseIf()(focus.Exactly(FOCUS_EFFECTUNIT2)):
                UnitManagerApp.setContent(g_effectunit_2, EPD(g_effectunit_2.getValueAddr()))
                appManager.startApplication(UnitManagerApp)
            if EUDElseIf()(focus.Exactly(FOCUS_EFFECTUNIT3)):
                UnitManagerApp.setContent(g_effectunit_3, EPD(g_effectunit_3.getValueAddr()))
                appManager.startApplication(UnitManagerApp)
            if EUDElseIf()(focus.Exactly(FOCUS_OBSTACLEUNIT)):
                UnitManagerApp.setContent(g_obstacleunit, EPD(g_obstacleunit.getValueAddr()))
                appManager.startApplication(UnitManagerApp)
            if EUDElseIf()(focus.Exactly(FOCUS_RUNNER_FORCE)):
                PlayerSelectorApp.setContent(g_runnerforce, EPD(g_runnerforce.getValueAddr()))
                appManager.startApplication(PlayerSelectorApp)
            if EUDElseIf()(focus.Exactly(FOCUS_RUNNER_UNIT)):
                UnitManagerApp.setContent(g_runnerunit, EPD(g_runnerunit.getValueAddr()))
                appManager.startApplication(UnitManagerApp)
            if EUDElseIf()(focus.Exactly(FOCUS_START_LOCATION)):
                LocationManagerApp.setContent(g_start_location, EPD(g_start_location.getValueAddr()))
                appManager.startApplication(LocationManagerApp)
            EUDEndIf()
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
        writer.write_f("Start location: %E\n")
        write.write(0)