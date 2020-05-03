'''
TUI - Configuring
 1. Bound Editor - Exporter (Bridge Client required)
 2. Death Unit used as timer (U) - {Cave}
 3. Turbo mode (T) - eudturbo, turbo, nothing
 4.
 5. Press CTRL+Y to EXPORT
 6.

TUI - Exporting
 1. Bound Editor - Exporter (Bridge Client required)
 2. Sent %D bytes / total %D bytes
 3.
'''


from eudplib import *
from repl import (
    Application,
    writeUnit
)

from ..unit import UnitManagerApp
from . import (
    appManager,
    g_effectplayer,
    p_count,
    p_actionCount,
    p_actionArrayEPD,
    p_waitValue
)
from repl.resources.scmdtrigwriter import writeTrigger

MODE_CONFIG    = 0
MODE_EXPORTING = 1
mode = EUDVariable(MODE_CONFIG)

TURBO_EUD     = 0
TURBO_NORMAL  = 1
TURBO_NOTHING = 2
TURBO_END     = 3
v_turbo_mode = EUDVariable()
v_death_unit = EUDVariable(EncodeUnit("Cave"))

storage = Db(200000)
remaining_bytes = EUDVariable(0)
written = EUDVariable(0)

writer = appManager.getWriter()

def writeBoundTriggers():
    global writer
    writer.seekepd(EPD(storage))

    # turbo, timer, ...
    if EUDIf()(v_turbo_mode.Exactly(TURBO_EUD)):
        writeTrigger(
            g_effectplayer,
            [Always()],
            ["MemoryAddr(0x6509A0, Set To, 0);\n"]
        )
    if EUDElseIf()(v_turbo_mode.Exactly(TURBO_NORMAL)):
        for i in range(3):
            writeTrigger(
                g_effectplayer,
                [Always()],
                ["Wait(0);\n" for _ in range(63)]
            )
    EUDEndIf()

    # main bound triggers
    next_timer = EUDVariable()
    next_timer << 0
    pattern_id = EUDVariable()
    pattern_id << 0
    if EUDInfLoop()():
        # for each pattern...
        EUDBreakIf(pattern_id >= p_count)

        cnt, action_epd = p_actionCount[pattern_id], p_actionArrayEPD[pattern_id]
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

            writeTrigger(
                g_effectplayer,
                [Deaths(g_effectplayer, Exactly, next_timer, v_death_unit)],
                (num_actions_to_send, action_epd)
            )

            rem_action_count -= num_actions_to_send
            action_epd += num_actions_to_send * (32//4)
        EUDEndInfLoop()

        next_timer += p_waitValue[pattern_id]
        pattern_id += 1
    EUDEndInfLoop()

    # making loop
    writeTrigger(
        g_effectplayer,
        [Always()],
        [SetDeaths(g_effectplayer, Add, 1, v_death_unit)]
    )
    writeTrigger(
        g_effectplayer,
        [Deaths(g_effectplayer, Exactly, next_timer, v_death_unit)],
        [SetDeaths(g_effectplayer, SetTo, 0, v_death_unit)]
    )

    writer.write(0)

    written << 0
    remaining_bytes << (writer.getoffset() - storage)

class ExporterApp(Application):
    def loop(self):
        global written, remaining_bytes, v_turbo_mode

        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
            EUDReturn()
        EUDEndIf()

        if EUDIf()(mode == MODE_CONFIG):
            if EUDIf()(appManager.keyPress("Y", hold = ["LCTRL"])):
                mode << MODE_EXPORTING
                writeBoundTriggers()
            if EUDElseIf()(appManager.keyPress("U")):
                UnitManagerApp.setContent(v_death_unit, EPD(v_death_unit.getValueAddr()))
                appManager.startApplication(UnitManagerApp)
            if EUDElseIf()(appManager.keyPress("T")):
                v_turbo_mode += 1
                Trigger(
                    conditions = v_turbo_mode.Exactly(TURBO_END),
                    actions = v_turbo_mode.SetNumber(0)
                )
            EUDEndIf()
        if EUDElse()(): # MODE_EXPORTING
            new_written = appManager.exportAppOutputToBridge(storage + written, remaining_bytes)

            remaining_bytes -= new_written
            written += new_written
            if EUDIf()(remaining_bytes == 0):
                mode << MODE_CONFIG
            EUDEndIf()
        EUDEndIf()
        appManager.requestUpdate()

    def print(self, writer):
        writer.write_f("Bound Editor - Exporter (Bridge Client required)\n")
        if EUDIf()(mode == MODE_CONFIG):
            writer.write_f("Death Unit used as timer (U): ")
            writeUnit(v_death_unit)
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
