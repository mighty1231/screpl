from eudplib import *

from screpl.apps.repl import REPL
from screpl.apps.logger import Logger
from screpl.core.appcommand import AppCommand
from screpl.main import get_app_manager
from eudplib.core.mapdata.stringmap import strmap

from .intacttrigger import IntactTrigger

# initialize variables
app_manager = get_app_manager()
STRSection = EUDVariable()
STRSection_end = EUDVariable()

def get_string_from_id(sid):
    return strmap.GetString(sid)

@EUDFunc
def f_epd2ptr(epd):
    return 0x58A364 + epd * 4

@EUDFunc
def logger_log_trigger(epd):
    ptr = f_epd2ptr(epd)
    with Logger.get_multiline_writer("Trigger") as logwriter:
        logwriter.write_f("Trigger %H next %H flag: ", ptr, f_dwread_epd(epd + 1))

        flags = f_dwread_epd(epd + (8 + 16*20 + 64*32) // 4)
        if EUDIf()(flags.ExactlyX(0x02, 0x02)):
            logwriter.write_f("IgnoreDefeat ")
        EUDEndIf()
        if EUDIf()(flags.ExactlyX(0x04, 0x04)):
            logwriter.write_f("PreserveTrigger ")
        EUDEndIf()
        if EUDIf()(flags.ExactlyX(0x08, 0x08)):
            logwriter.write_f("IgnoreExecution ")
        EUDEndIf()
        if EUDIf()(flags.ExactlyX(0x10, 0x10)):
            logwriter.write_f("SkipUIActions ")
        EUDEndIf()
        if EUDIf()(flags.ExactlyX(0x20, 0x20)):
            logwriter.write_f("PausedGame ")
        EUDEndIf()
        if EUDIf()(flags.ExactlyX(0x40, 0x40)):
            logwriter.write_f("DisableWaitSkip ")
        EUDEndIf()
        logwriter.write_f("\nCondition\n")
        cur_epd = epd + 8 // 4
        if EUDLoopN()(16):
            # check condtype = 0
            EUDBreakIf(MemoryXEPD(cur_epd + 3, Exactly, 0, 0xFF000000))
            logwriter.write_f(" - ")
            logwriter.write_condition_epd(cur_epd)
            logwriter.write_f("\n")

            cur_epd += 20 // 4
        EUDEndLoopN()

        logwriter.write_f("\nAction\n")
        cur_epd << epd + (8 + 16*20) // 4
        if EUDLoopN()(64):
            # check acttype = 0
            EUDBreakIf(MemoryXEPD(cur_epd + 6, Exactly, 0, 0xFF0000))
            logwriter.write_f(" - ")
            logwriter.write_action_epd(cur_epd)
            logwriter.write_f("\n")

            cur_epd += 32 // 4
        EUDEndLoopN()
        logwriter.write(0)

@EUDFunc
def _disassemble_and_log_trigger(trig_id, trig_epd):
    trig_conditions = [Forward() for _ in range(16)]
    trig_on_true = [Forward() for _ in range(16)]
    trig_on_false = [Forward() for _ in range(16)]
    trig_next_cond = [Forward() for _ in range(16)]
    trig_branch, trig_condition_fail, trig_action = [Forward() for _ in range(3)]
    # condition_count = EUDVariable(0)
    # condition_states = EUDArray(16)

    # fill 0
    DoActions(
        # [condition_count.SetNumber(0)]
        # + [SetMemory(condition_states + i, SetTo, 0) for i in range(16)]
        [SetMemory(trig_action + 8 + 16*20 + i, SetTo, 0) for i in range(0, 32*64, 4)]
    )

    # disassemble trigger - conditions
    for i in range(16):
        f_repmovsd_epd(
            EPD(trig_conditions[i] + 8),
            trig_epd + (8 + i*20)//4,
            20//4
        )

    # actions
    f_repmovsd_epd(
        EPD(trig_action + 8 + 16*20),
        trig_epd + (8 + 16*20)//4,
        (2408 - 8 - 16*20) // 4
    )

    DoActions(
        [SetNextPtr(trig_conditions[i], trig_on_false[i]) for i in range(16)]
        + [SetNextPtr(trig_branch, trig_action)]
    )

    if EUDExecuteOnce()():
        logger_log_trigger(trig_epd)
        logger_log_trigger(EPD(trig_conditions[0]))
        logger_log_trigger(EPD(trig_conditions[1]))
        logger_log_trigger(EPD(trig_action))
    EUDEndExecuteOnce()

    writer = Logger.get_writer()
    writer.write_f("trig[%D] ", trig_id)
    for i in range(16):
        # check condtype == 0
        EUDJumpIf(
            MemoryXEPD(EPD(trig_conditions[i] + 8 + 0xC), Exactly, 0, 0xFF000000),
            trig_branch
        )
        trig_conditions[i] << IntactTrigger(
            conditions = [],
            actions = [SetNextPtr(trig_conditions[i], trig_on_true[i])]
        )
        trig_on_false[i] << NextTrigger()
        writer.write_f("{}:X ".format(i))
        RawTrigger(
            nextptr = trig_next_cond[i],
            actions = SetNextPtr(trig_branch, trig_condition_fail)
        )

        trig_on_true[i] << NextTrigger()
        writer.write_f("{}:O ".format(i))

        trig_next_cond[i] << NextTrigger()

    trig_branch << RawTrigger()
    trig_action << IntactTrigger()
    trig_condition_fail << NextTrigger()

    writer.write(0)


class TrigInliningManager:
    def __init__(self):
        self.sigid = None
        self.triggers = []
        self.trig_count = 0

    def register_trigger(self, trigger):
        assert isinstance(trigger, bytes)
        trig_object = IntactTrigger(trigSection=trigger)

        # build inlining player code
        player_code = 0
        for i in range(27):
            if trigger[320 + 2048 + 4 + i]:
                player_code |= 1 << i

        inline_trig = (bytes(20)
                       + i2b4(0x10978d4a)
                       + i2b4(player_code)
                       + ('screpl_log_trigger(%d)'
                          % self.trig_count).encode())
        inline_trig += bytes(2400-len(inline_trig))

        self.trig_count += 1
        self.triggers.append(trig_object)

        return inline_trig

    def log_trigger(self, trig_id):
        trigger = self.triggers[trig_id]
        _disassemble_and_log_trigger(trig_id, EPD(trigger))

    def find_signature_and_update(self):
        """Find trigger with debugging signature

        Find a trigger with the first action, Comment("screpl-trigger")
        """
        orig_triggers = GetChkTokenized().getsection(b'TRIG')
        assert len(orig_triggers) % 2400 == 0

        offset = 0
        while offset < len(orig_triggers):
            trig = orig_triggers[offset:offset+2400]

            # parse the first action
            action0 = trig[16*20:16*20+32]
            acttype = action0[26]

            if acttype == 47: # Comment
                strid = b2i4(action0, 4)
                string = get_string_from_id(strid)
                if string == b'screpl-trigger':
                    assert self.sigid is None or self.sigid == strid, \
                        "String table is screwed"
                    self.sigid = strid

                    # register trigger and update
                    new_trig = self.register_trigger(trig)
                    orig_triggers = (orig_triggers[:offset]
                                     + new_trig
                                     + orig_triggers[offset+2400:])

            offset += 2400
        GetChkTokenized().setsection(b'TRIG', orig_triggers)

def plugin_setup():
    STRSection << f_dwread_epd(EPD(0x5993D4))
    STRSection_end << STRSection + app_manager.get_strx_section_size()

    tsm = TrigInliningManager()
    tsm.find_signature_and_update()

    EUDRegisterObjectToNamespace("screpl_log_trigger", tsm.log_trigger)

    # make commands
    from .manager import TriggerManagerApp

    @AppCommand([])
    def start_command(self):
        app_manager.start_application(TriggerManagerApp)

    REPL.add_command('trigger', start_command)
