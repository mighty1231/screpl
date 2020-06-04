from eudplib import *

from screpl.apps.repl import REPL
from screpl.apps.logger import Logger
from screpl.core.appcommand import AppCommand
from screpl.main import get_app_manager
from screpl.utils.debug import f_raise_error
from eudplib.core.mapdata.stringmap import strmap

from .entry import MaximumCircularBuffer, ResultEntry

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

@EUDTypedFunc([None, MaximumCircularBuffer(ResultEntry)])
def _disassemble_and_log_trigger(trig_epd, entry_table):
    trig_conditions = [Forward() for _ in range(16)]
    trig_copy = Forward()

    cond_count = EUDVariable(0)
    cond_bools = EUDArray(16)
    cond_values = EUDArray(16)

    # initialize
    DoActions(
        [cond_count.SetNumber(0)]
        + [SetMemory(cond_bools + i, SetTo, 0) for i in range(16)]
        + [SetMemory(cond_values + i, SetTo, 0) for i in range(16)]
    )

    # disassemble trigger - conditions
    for i in range(16):
        f_repmovsd_epd(
            EPD(trig_conditions[i]),
            trig_epd + (8 + i*20)//4,
            20//4
        )

    # trigger
    f_repmovsd_epd(EPD(trig_copy)+2, trig_epd+2, 2400//4)

    if EUDExecuteOnce()():
        logger_log_trigger(trig_epd)
        logger_log_trigger(EPD(trig_conditions[0]-8))
        logger_log_trigger(EPD(trig_conditions[1]-8))
        logger_log_trigger(EPD(trig_copy))
    EUDEndExecuteOnce()

    for i in range(16):
        # check condtype == 0
        EUDJumpIf(
            MemoryXEPD(EPD(trig_conditions[i] + 0xC), Exactly, 0, 0xFF000000),
            trig_copy
        )
        if EUDIf()(trig_conditions[i] << Memory(0, Exactly, 0)):
            cond_bools[i] = 1
        if EUDElse()():
            # evaluate exact value
            condtype = f_bread_epd(EPD(trig_conditions[i] + 0xC), 3)
            cond_values[i] = 1123 # @TODO
        EUDEndIf()
        cond_count += 1

    # call original trigger
    trig_copy << IntactTrigger()

    # update
    trig_end = Forward()
    if EUDIfNot()(entry_table.empty()):
        last_entry = entry_table.last()
        if EUDIf()(last_entry.update(cond_count,
                                     EPD(cond_bools),
                                     EPD(cond_values)) == 0):
            EUDJump(trig_end)
        EUDEndIf()
    EUDEndIf()

    # add entry
    new_entry = ResultEntry.cast(f_dwread_epd(
        entry_table.push_and_get_reference()))
    tick = f_getgametick()
    new_entry.start_tick = tick
    new_entry.end_tick = tick
    new_entry.cond_count = cond_count
    f_repmovsd_epd(new_entry.cond_bools_epd, EPD(cond_bools), cond_count)
    f_repmovsd_epd(new_entry.cond_values_epd, EPD(cond_values), cond_count)

    trig_end << NextTrigger()


class TrigInliningManager:
    def __init__(self):
        self.sigid = None
        self.triggers = []
        self.trig_count = 0

        # called result tables
        self.result_tables = []
        self.force_players = [set(), set(), set(), set()]
        for pid in range(8):
            self.force_players[GetPlayerInfo(pid).force].add(pid)
        EUDRegisterObjectToNamespace("screpl_log_trigger", self.log_trigger)

    def register_trigger(self, trigger):
        assert isinstance(trigger, bytes)

        # it should not have any wait action
        for i in range(64):
            action = trigger[16*20+32*i:16*20+32*(i+1)]
            acttype = action[26]
            if acttype == 0:
                break
            if acttype == 4:
                raise ValueError("Trigger with Wait() action cannot be inlined")

        trig_object = IntactTrigger(trigSection=trigger)

        # build inlining player code
        effplayers = set() # 0 ~ 8
        player_code = 0
        for pid in range(27):
            if trigger[320 + 2048 + 4 + pid]:
                player_code |= 1 << pid
                if pid <= 8:
                    effplayers.add(pid)
                elif pid == EncodePlayer(AllPlayers):
                    effplayers |= set(range(8))
                elif pid in list(map(EncodePlayer,
                                     [Force1, Force2, Force3, Force4])):
                    effplayers |= self.force_players[pid-EncodePlayer(Force1)]
                else:
                    raise ValueError(
                        "Unknown behavior on trigger with player %d" % pid)

        # create result entries
        result_entries = {}
        for pid in effplayers:
            result_entries[pid] = MaximumCircularBuffer(ResultEntry).construct_w_empty([
                ResultEntry.construct() for _ in range(10)
            ])

        # construct inline trigger
        inline_trig = (bytes(20)
                       + i2b4(0x10978d4a)
                       + i2b4(player_code)
                       + ('screpl_log_trigger(%d, f_getcurpl())'
                          % self.trig_count).encode())
        inline_trig += bytes(2400-len(inline_trig))

        self.trig_count += 1
        self.triggers.append(trig_object)
        self.result_tables.append(result_entries)

        return inline_trig

    def log_trigger(self, trig_id, player_id):
        trigger = self.triggers[trig_id]
        result_table = self.result_tables[trig_id]
        _br = EUDIf
        result_entry = EUDVariable()
        for ep, entry in result_table.items():
            _br()(player_id.Exactly(ep))
            result_entry << entry
            _br = EUDElseIf
        if EUDElse()():
            f_raise_error("screpl-trigger trig id %D - player id %D unknown",
                          trig_id, player_id)
        EUDEndIf()
        _disassemble_and_log_trigger(EPD(trigger), result_entry)

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

    # make commands
    from .manager import TriggerManagerApp

    @AppCommand([])
    def start_command(self):
        app_manager.start_application(TriggerManagerApp)

    REPL.add_command('trigger', start_command)
