"""
Expected TUI:

.. code-block:: text

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
"""

from eudplib import *

from screpl.apps.selector import SelectorApp
from screpl.core.appcommand import AppCommand
from screpl.core.application import Application
from screpl.encoder.const import ArgEncNumber
import screpl.resources.table.tables as tb

from screpl.plugins.location.manager import LocationManagerApp
from screpl.plugins.unit.manager import UnitManagerApp

from . import (
    app_manager,
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
    write_player,
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
        if EUDIf()(app_manager.key_press("ESC")):
            app_manager.request_destruct()
        if EUDElseIf()(app_manager.key_press("F7")):
            Trigger(
                conditions=focus.Exactly(0),
                actions=focus.SetNumber(FOCUS_END)
            )
            DoActions(focus.SubtractNumber(1))
        if EUDElseIf()(app_manager.key_press("F8")):
            DoActions(focus.AddNumber(1))
            Trigger(
                conditions=focus.Exactly(FOCUS_END),
                actions=focus.SetNumber(0)
            )
        if EUDElseIf()(app_manager.key_press("E", hold=["LCTRL"])):
            if EUDIf()(focus.Exactly(FOCUS_EFFECTPLAYER)):
                SelectorApp.set_content(tb.Player, g_effectplayer)
                app_manager.start_application(SelectorApp)
            if EUDElseIf()(focus.Exactly(FOCUS_EFFECTUNIT1)):
                UnitManagerApp.set_content(
                    g_effectunit_1,
                    EPD(g_effectunit_1.getValueAddr()))
                app_manager.start_application(UnitManagerApp)
            if EUDElseIf()(focus.Exactly(FOCUS_EFFECTUNIT2)):
                UnitManagerApp.set_content(
                    g_effectunit_2,
                    EPD(g_effectunit_2.getValueAddr()))
                app_manager.start_application(UnitManagerApp)
            if EUDElseIf()(focus.Exactly(FOCUS_EFFECTUNIT3)):
                UnitManagerApp.set_content(
                    g_effectunit_3,
                    EPD(g_effectunit_3.getValueAddr()))
                app_manager.start_application(UnitManagerApp)
            if EUDElseIf()(focus.Exactly(FOCUS_OBSTACLEUNIT)):
                UnitManagerApp.set_content(
                    g_obstacle_unit,
                    EPD(g_obstacle_unit.getValueAddr()))
                app_manager.start_application(UnitManagerApp)
            if EUDElseIf()(focus.Exactly(FOCUS_RUNNER_FORCE)):
                SelectorApp.set_content(tb.Player, g_runner_force)
                app_manager.start_application(SelectorApp)
            if EUDElseIf()(focus.Exactly(FOCUS_RUNNER_UNIT)):
                UnitManagerApp.set_content(
                    g_runner_unit,
                    EPD(g_runner_unit.getValueAddr()))
                app_manager.start_application(UnitManagerApp)
            if EUDElseIf()(focus.Exactly(FOCUS_START_LOCATION)):
                LocationManagerApp.set_content(
                    g_start_location,
                    EPD(g_start_location.getValueAddr()))
                app_manager.start_application(LocationManagerApp)
            if EUDElseIf()(focus.Exactly(FOCUS_OBSCREATE_PATTERN)):
                DoActions(g_obstacle_createpattern.AddNumber(1))
                Trigger(
                    conditions=g_obstacle_createpattern.Exactly(
                        OBSTACLE_CREATEPATTERN_END),
                    actions=g_obstacle_createpattern.SetNumber(0))
            if EUDElseIf()(focus.Exactly(FOCUS_OBSDESTRUCT_PATTERN)):
                DoActions(g_obstacle_destructpattern.AddNumber(1))
                Trigger(
                    conditions=g_obstacle_destructpattern.Exactly(
                        OBSTACLE_DESTRUCTPATTERN_END),
                    actions=g_obstacle_destructpattern.SetNumber(0))
            EUDEndIf()
        EUDEndIf()
        app_manager.request_update()

    def print(self, writer):
        writer.write_f(
            "\x16Bound Editor Options - F7, F8 to navigate, CTRL+E to modify\n"
            "Effect player: %C%:constant;\n"
            "\x16Effect unit 1/2/3: %C%:unit;\x16 / %C%:unit;\x16 / %C%:unit;\n"
            "\x16Obstacle unit: %C%:unit;\n"
            "\x16Runner force: %C%:constant;\n"
            "\x16Runner unit: %C%:unit;\n"
            "\x16Start location: %C%:location;\n",
            EUDTernary(focus==FOCUS_EFFECTPLAYER)(0x11)(0x16),
            (EPD(tb.Player), g_effectplayer),
            EUDTernary(focus==FOCUS_EFFECTUNIT1)(0x11)(0x16),
            (g_effectunit_1, ),
            EUDTernary(focus==FOCUS_EFFECTUNIT2)(0x11)(0x16),
            (g_effectunit_2, ),
            EUDTernary(focus==FOCUS_EFFECTUNIT3)(0x11)(0x16),
            (g_effectunit_3, ),
            EUDTernary(focus==FOCUS_OBSTACLEUNIT)(0x11)(0x16),
            (g_obstacle_unit, ),
            EUDTernary(focus==FOCUS_RUNNER_FORCE)(0x11)(0x16),
            (EPD(tb.Player), g_runner_force),
            EUDTernary(focus==FOCUS_RUNNER_UNIT)(0x11)(0x16),
            (g_runner_unit, ),
            EUDTernary(focus==FOCUS_START_LOCATION)(0x11)(0x16),
            (g_start_location, ))

        writer.write_f("\x16On obstacle be created, runner be ")
        writer.write(EUDTernary(focus==FOCUS_OBSCREATE_PATTERN)(0x11)(0x16))
        for v, s in [(OBSTACLE_CREATEPATTERN_KILL, "killed\n"),
                     (OBSTACLE_CREATEPATTERN_REMOVE, "removed\n"),
                     (OBSTACLE_CREATEPATTERN_ALIVE, "alive\n")]:
            if EUDIf()(g_obstacle_createpattern.Exactly(v)):
                writer.write_f(s)
            EUDEndIf()

        writer.write_f("\x16On obstacle be destructed, obstacle be ")
        writer.write(EUDTernary(focus==FOCUS_OBSDESTRUCT_PATTERN)(0x11)(0x16))
        for v, s in [(OBSTACLE_DESTRUCTPATTERN_KILL, "killed\n"),
                     (OBSTACLE_DESTRUCTPATTERN_REMOVE, "removed\n")]:
            if EUDIf()(g_obstacle_destructpattern.Exactly(v)):
                writer.write_f(s)
            EUDEndIf()

        writer.write(0)
