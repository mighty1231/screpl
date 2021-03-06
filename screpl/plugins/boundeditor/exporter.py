"""ExporterApp

Expected TUI - Configuring

.. code-block:: text

    1. Bound Editor - Exporter (Bridge Client required)
    2. Death Unit used as timer (U) - {Cave}
    3. Turbo mode (T) - eudturbo, turbo, nothing
    4.
    5. Press CTRL+Y to EXPORT
    6.

Expected TUI - Exporting

.. code-block:: text

    1. Bound Editor - Exporter (Bridge Client required)
    2. Sent %D bytes / total %D bytes
    3.
"""

from eudplib import *

from screpl.core.application import Application

from screpl.plugins.unit.manager import UnitManagerApp
from . import (
    app_manager,
    g_effectplayer,
    p_count,
    p_action_count,
    p_action_array_epd,
    p_wait_value,
    g_runner_force,
    g_runner_unit,
    g_start_location
)
from screpl.main import get_main_writer

MODE_CONFIG    = 0
MODE_EXPORTING = 1
mode = EUDVariable(MODE_CONFIG)

TURBO_EUD     = 0
TURBO_NORMAL  = 1
TURBO_NOTHING = 2
TURBO_END     = 3
v_turbo_mode = EUDVariable()
v_death_unit = EUDVariable(EncodeUnit("Cave (Unused)"))

storage = Db(200000)
remaining_bytes = EUDVariable(0)
written = EUDVariable(0)

writer = get_main_writer()

def write_bound_triggers():
    global writer
    writer.seekepd(EPD(storage))

    writer.write_scmd_trigger(
        g_runner_force,
        [Always()],
        ["Comment(\"Score\");\n",
         "Leader Board Points(\"\\x007Deaths\", Custom);\n",
         "Leaderboard Computer Players(disabled);\n",
         SetScore(g_runner_force, SetTo, 0, Custom)],
        preserved = False
    )
    writer.write_scmd_trigger(
        g_effectplayer,
        ["Command(\"Player 12\", \"Men\", At least, 1);\n"],
        ["Remove Unit(\"Player 12\", \"Men\");\n"]
    )
    writer.write_scmd_trigger(
        AllPlayers,
        [Always()],
        ["Set Alliance Status(\"All players\", Ally);\n"],
        preserved = False
    )

    # main bound triggers
    next_timer, pattern_id = EUDCreateVariables(2)
    next_timer << 0
    pattern_id << 0
    if EUDInfLoop()():
        # for each pattern...
        EUDBreakIf(pattern_id >= p_count)

        cnt, action_epd = p_action_count[pattern_id], p_action_array_epd[pattern_id]
        rem_action_count = EUDVariable()
        rem_action_count << cnt

        # flush action buffer
        if EUDInfLoop()():
            EUDBreakIf(rem_action_count == 0)

            # with preserve trigger, maximum 63 actions
            num_actions_to_send = EUDVariable()
            if EUDIf()(rem_action_count >= 63):
                num_actions_to_send << 63
            if EUDElse()():
                num_actions_to_send << rem_action_count
            EUDEndIf()

            writer.write_scmd_trigger(
                g_effectplayer,
                ["// EXTRA_CONDITION\n",
                 Deaths(g_effectplayer, Exactly, next_timer, v_death_unit)],
                (num_actions_to_send, action_epd)
            )

            rem_action_count -= num_actions_to_send
            action_epd += num_actions_to_send * (32//4)
        EUDEndInfLoop()

        next_timer += p_wait_value[pattern_id]
        pattern_id += 1
    EUDEndInfLoop()

    # making loop
    writer.write_scmd_trigger(
        g_effectplayer,
        ["// EXTRA_CONDITION\n",
         Always()],
        [SetDeaths(g_effectplayer, Add, 1, v_death_unit)]
    )
    writer.write_scmd_trigger(
        g_effectplayer,
        ["// EXTRA_CONDITION\n",
         Deaths(g_effectplayer, Exactly, next_timer, v_death_unit)],
        [SetDeaths(g_effectplayer, SetTo, 0, v_death_unit)]
    )

    # death condition
    writer.write_scmd_trigger(
        g_runner_force,
        ["// EXTRA_CONDITION\n",
         Command(CurrentPlayer, Exactly, 0, g_runner_unit)],
        [CreateUnit(1, g_runner_unit, g_start_location, CurrentPlayer),
         SetScore(CurrentPlayer, Add, 1, Custom)]
    )

    # turbo, timer, ...
    if EUDIf()(v_turbo_mode.Exactly(TURBO_EUD)):
        writer.write_scmd_trigger(
            g_effectplayer,
            [Always()],
            ["MemoryAddr(0x6509A0, Set To, 0);\n"]
        )
    if EUDElseIf()(v_turbo_mode.Exactly(TURBO_NORMAL)):
        for _ in range(3):
            writer.write_scmd_trigger(
                g_effectplayer,
                [Always()],
                ["Wait(0);\n" * 63]
            )
    EUDEndIf()

    writer.write(0)

    written << 0
    remaining_bytes << (writer.getoffset() - storage)

class ExporterApp(Application):
    def loop(self):
        global written, remaining_bytes, v_turbo_mode

        if EUDIf()(app_manager.key_press("ESC")):
            app_manager.request_destruct()
        EUDEndIf()

        if EUDIf()(mode == MODE_CONFIG):
            if EUDIf()(app_manager.key_press("Y", hold=["LCTRL"])):
                mode << MODE_EXPORTING
                write_bound_triggers()
            if EUDElseIf()(app_manager.key_press("U")):
                UnitManagerApp.set_content(v_death_unit, EPD(v_death_unit.getValueAddr()))
                app_manager.start_application(UnitManagerApp)
            if EUDElseIf()(app_manager.key_press("T")):
                v_turbo_mode += 1
                Trigger(
                    conditions=v_turbo_mode.Exactly(TURBO_END),
                    actions=v_turbo_mode.SetNumber(0)
                )
            EUDEndIf()
        if EUDElse()(): # MODE_EXPORTING
            new_written = app_manager.send_app_output_to_bridge(storage + written, remaining_bytes)

            remaining_bytes -= new_written
            written += new_written
            if EUDIf()(app_manager.synchronize([
                    (EPD(remaining_bytes.getValueAddr()), Exactly, 0)])):
                mode << MODE_CONFIG
            EUDEndIf()
        EUDEndIf()
        app_manager.request_update()

    def print(self, writer):
        writer.write_f("Bound Editor - Exporter (Bridge Client required)\n")
        if EUDIf()(mode == MODE_CONFIG):
            writer.write_f("Death Unit used as timer (U): ")
            writer.write_unit(v_death_unit)
            writer.write_f("\nTurbo mode (T) - ")

            if EUDIf()(v_turbo_mode == TURBO_EUD):
                writer.write(0x11)
            if EUDElse()():
                writer.write(2)
            EUDEndIf()
            writer.write_f("eudturbo ")
            if EUDIf()(v_turbo_mode == TURBO_NORMAL):
                writer.write(0x11)
            if EUDElse()():
                writer.write(2)
            EUDEndIf()
            writer.write_f("turbo ")
            if EUDIf()(v_turbo_mode == TURBO_NOTHING):
                writer.write(0x11)
            if EUDElse()():
                writer.write(2)
            EUDEndIf()
            writer.write_f("noturbo ")

            writer.write_f("\n\x16Press CTRL+Y to EXPORT\n")

        if EUDElse()():
            writer.write_f("\x13Sent %D bytes / Remaining %D bytes\n\n\n\n", written, remaining_bytes)
        EUDEndIf()
        writer.write(0)
