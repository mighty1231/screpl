'''
 1. BoundEditor Options
 2. Effect player: P8
 3. Effect unit 1/2/3: Zerg Scourge, Zerg Overlord, Terran Battlecruiser
 4. Obstacle unit: Psi Emitter
 5. Runner force: Force1
 6. Runner unit: Zerg Zergling
 7. Start location: location
 8. On obstacle be created, runner be killed/removed/alive
 9. On obstacle be destructed, kill/remove it
10.
11.
'''

from eudplib import *
from repl import (
    Application,
    AppTypedMethod,
    AppCommand,
    argEncNumber,
    writeUnit,
    writeLocation,
    PlayerSelectorApp
)

from ..location import LocationManagerApp
from ..unit import UnitManagerApp

from . import (
    appManager,
    g_effectplayer,
    g_effectunit_1,
    g_effectunit_2,
    g_effectunit_3,
    g_obstacle_unit,
    g_start_location,
    g_runner_force,
    g_runner_unit,
    OBSTACLE_CREATEPATTERN_KILL,
    OBSTACLE_CREATEPATTERN_REMOVE,
    OBSTACLE_CREATEPATTERN_ALIVE,
    OBSTACLE_CREATEPATTERN_END,
    g_obstacle_createpattern,
    OBSTACLE_DESTRUCTPATTERN_KILL,
    OBSTACLE_DESTRUCTPATTERN_REMOVE,
    OBSTACLE_DESTRUCTPATTERN_END,
    g_obstacle_destructpattern,
    writePlayer
)

FOCUS_EFFECTPLAYER      = 0
FOCUS_EFFECTUNIT1       = 1
FOCUS_EFFECTUNIT2       = 2
FOCUS_EFFECTUNIT3       = 3
FOCUS_OBSTACLEUNIT      = 4
FOCUS_RUNNER_FORCE      = 5
FOCUS_RUNNER_UNIT       = 6
FOCUS_START_LOCATION    = 7
FOCUS_OBSCREATE_PATTERN = 8
FOCUS_OBSDESTRUCT_PATTERN = 9
FOCUS_END               = 10

focus_modes = [
    FOCUS_EFFECTPLAYER,
    FOCUS_EFFECTUNIT1,
    FOCUS_EFFECTUNIT2,
    FOCUS_EFFECTUNIT3,
    FOCUS_OBSTACLEUNIT,
    FOCUS_RUNNER_FORCE,
    FOCUS_RUNNER_UNIT,
    FOCUS_START_LOCATION,
    FOCUS_OBSCREATE_PATTERN,
    FOCUS_OBSDESTRUCT_PATTERN
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
                UnitManagerApp.setContent(g_obstacle_unit, EPD(g_obstacle_unit.getValueAddr()))
                appManager.startApplication(UnitManagerApp)
            if EUDElseIf()(focus.Exactly(FOCUS_RUNNER_FORCE)):
                PlayerSelectorApp.setContent(g_runner_force, EPD(g_runner_force.getValueAddr()))
                appManager.startApplication(PlayerSelectorApp)
            if EUDElseIf()(focus.Exactly(FOCUS_RUNNER_UNIT)):
                UnitManagerApp.setContent(g_runner_unit, EPD(g_runner_unit.getValueAddr()))
                appManager.startApplication(UnitManagerApp)
            if EUDElseIf()(focus.Exactly(FOCUS_START_LOCATION)):
                LocationManagerApp.setContent(g_start_location, EPD(g_start_location.getValueAddr()))
                appManager.startApplication(LocationManagerApp)
            if EUDElseIf()(focus.Exactly(FOCUS_OBSCREATE_PATTERN)):
                DoActions(g_obstacle_createpattern.AddNumber(1))
                Trigger(
                    conditions = g_obstacle_createpattern.Exactly(OBSTACLE_CREATEPATTERN_END),
                    actions = g_obstacle_createpattern.SetNumber(0)
                )
            if EUDElseIf()(focus.Exactly(FOCUS_OBSDESTRUCT_PATTERN)):
                DoActions(g_obstacle_destructpattern.AddNumber(1))
                Trigger(
                    conditions = g_obstacle_destructpattern.Exactly(OBSTACLE_DESTRUCTPATTERN_END),
                    actions = g_obstacle_destructpattern.SetNumber(0)
                )
            EUDEndIf()
        EUDEndIf()
        appManager.requestUpdate()

    def print(self, writer):
        def _emphasize(val):
            if EUDIf()(focus.Exactly(val)):
                writer.write(0x11)
            if EUDElse()():
                writer.write(0x2)
            EUDEndIf()

        writer.write_f("BoundEditor Options - F7, F8 to navigate, INSERT to modify\n")
        writer.write_f("Effect player: ")
        _emphasize(FOCUS_EFFECTPLAYER)
        writePlayer(g_effectplayer)

        writer.write_f("\x02\nEffect unit 1/2/3: ")
        _emphasize(FOCUS_EFFECTUNIT1)
        writeUnit(g_effectunit_1)
        writer.write_f("\x02, ")
        _emphasize(FOCUS_EFFECTUNIT2)
        writeUnit(g_effectunit_2)
        writer.write_f("\x02, ")
        _emphasize(FOCUS_EFFECTUNIT3)
        writeUnit(g_effectunit_3)

        writer.write_f("\x02\nobstacle unit: ")
        _emphasize(FOCUS_OBSTACLEUNIT)
        writeUnit(g_obstacle_unit)

        writer.write_f("\x02\nRunner Force: ")
        _emphasize(FOCUS_RUNNER_FORCE)
        writePlayer(g_runner_force)

        writer.write_f("\x02\nRunner unit: ")
        _emphasize(FOCUS_RUNNER_UNIT)
        writeUnit(g_runner_unit)

        writer.write_f("\x02\nStart location: ")
        _emphasize(FOCUS_START_LOCATION)
        writeLocation(g_start_location)

        writer.write_f("\x02\nOn obstacle be created, runner be ")
        _emphasize(FOCUS_OBSCREATE_PATTERN)
        for v, s in [(OBSTACLE_CREATEPATTERN_KILL, "killed"),
                (OBSTACLE_CREATEPATTERN_REMOVE, "removed"),
                (OBSTACLE_CREATEPATTERN_ALIVE, "alive")]:
            if EUDIf()(g_obstacle_createpattern.Exactly(v)):
                writer.write_f(s)
            EUDEndIf()

        writer.write_f("\x02\nOn obstacle be destructed, obstacle be ")
        _emphasize(FOCUS_OBSDESTRUCT_PATTERN)
        for v, s in [(OBSTACLE_DESTRUCTPATTERN_KILL, "killed"),
                (OBSTACLE_DESTRUCTPATTERN_REMOVE, "removed")]:
            if EUDIf()(g_obstacle_destructpattern.Exactly(v)):
                writer.write_f(s)
            EUDEndIf()

        writer.write(ord('\n'))
        writer.write(0)
