"""Trigger plugin

Enables condition checking on TRIG triggers

Log following TRIG triggers:

1. The first action of trigger is 'Comment("screpl-condcheck")'
2. No Wait() action.

For all trigger, it starts to log results of conditions for each players
P1 through P8. For comparison functions, it logs the exact value additionally.
"""
from eudplib import *

from screpl.apps.repl import REPL
from screpl.core.appcommand import AppCommand
from screpl.main import get_app_manager
from screpl.utils.debug import f_raise_error
from eudplib.core.mapdata.stringmap import strmap

from .entry import MaximumCircularBuffer, ResultEntry

from .intacttrigger import IntactTrigger

# initialize variables
app_manager = get_app_manager()
ENTRY_SIZE = 8

def get_string_from_id(sid):
    return strmap.GetString(sid)

@EUDFunc
def f_get_exact_amount(cond_epd):
    measure_condition = Forward()
    SeqCompute([
        (EPD(measure_condition) + k,
         SetTo,
         f_dwread_epd(cond_epd + k))
        for k in range(20//4)])

    # modify amount, comparison
    DoActions([SetMemoryEPD(EPD(measure_condition + 0x8), SetTo, 0),
               SetMemoryXEPD(EPD(measure_condition + 0xC),
                             SetTo,
                             EncodeComparison(AtLeast) * 0x10000,
                             0xFF0000)])

    # get maximum of x such that the condition with >= x holds
    k = EUDVariable()
    act0, act1 = Forward(), Forward()
    k << 0
    if EUDWhileNot()(k >= 32):
        EUDSwitch(k)
        for kval in range(32):
            EUDSwitchCase()(kval)
            SeqCompute([
                (EPD(act0 + 20), SetTo, 2 ** (31-kval)),
                (EPD(act1 + 20), SetTo, 2 ** (31-kval)),
            ])
            EUDBreak()
        EUDEndSwitch()

        DoActions(act0 << SetMemory(measure_condition + 0x8,
                                  Add,
                                  0)) # 2 ** (31-k)
        if EUDIfNot()(measure_condition << Memory(0, 0, 0)):
            DoActions(act1 << SetMemory(measure_condition + 0x8,
                                      Subtract,
                                      0)) # 2 ** (31-k)
        EUDEndIf()
        k += 1
    EUDEndWhile()
    return f_dwread_epd(EPD(measure_condition + 0x8))

@EUDTypedFunc([None, MaximumCircularBuffer(ResultEntry)])
def _condcheck_trigger(trigdb_epd, entry_table):
    trig_conditions = [Forward() for _ in range(16)]
    trig_copy = Forward()
    measure_conditions = [Forward() for _ in range(16)]

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
            trigdb_epd + i*20//4,
            20//4
        )

    # trigger
    f_repmovsd_epd(EPD(trig_copy)+2, trigdb_epd, 2400//4)

    for i in range(16):
        # check condtype == 0
        EUDJumpIf(
            MemoryXEPD(EPD(trig_conditions[i] + 0xC), Exactly, 0, 0xFF000000),
            trig_copy
        )

        # evaluate condition
        if EUDIf()(trig_conditions[i] << Memory(0, Exactly, 0)):
            cond_bools[i] = 1
        EUDEndIf()

        '''evaluate exact values on comparison type conditions

        * CountdownTimer (1)
        * Command (2)
        * Bring (3)
        * Accumulate (4)
        * Kills (5)
        * ElapsedTime (12)
        * Opponents (14)
        * Deaths (15)
        * Score (21)
        '''
        cond_type = f_bread_epd(EPD(trig_conditions[i] + 0xC), 3)
        is_comparison = EUDVariable()
        is_comparison << 0
        EUDSwitch(cond_type)
        for comp_cond_type in [1, 2, 3, 4, 5, 12, 14, 15, 21]:
            EUDSwitchCase()(comp_cond_type)
        is_comparison << 1
        EUDEndSwitch()
        if EUDIf()(is_comparison == 1): # cond check
            cond_values[i] = f_get_exact_amount(EPD(trig_conditions[i]))
        EUDEndIf()
        cond_count += 1

    # call original trigger
    trig_copy << IntactTrigger()

    # some flags may changed. update db
    f_repmovsd_epd(trigdb_epd, EPD(trig_copy)+2, 2400//4)

    # update result entries
    trig_end = Forward()
    if EUDIfNot()(entry_table.empty()):
        last_entry = entry_table.last()
        if EUDIf()(last_entry.update(cond_count,
                                     EPD(cond_bools),
                                     EPD(cond_values)) == 0):

            # update complete
            EUDJump(trig_end)
        EUDEndIf()
    EUDEndIf()

    # not matched to last entry. add a new entry
    new_entry = ResultEntry.cast(f_dwread_epd(
        entry_table.push_and_get_reference()))
    tick = f_getgametick()
    new_entry.start_tick = tick
    new_entry.end_tick = tick
    new_entry.cond_count = cond_count
    f_repmovsd_epd(new_entry.cond_bools_epd, EPD(cond_bools), cond_count)
    f_repmovsd_epd(new_entry.cond_values_epd, EPD(cond_values), cond_count)

    trig_end << NextTrigger()


class CondCheckTriggerManager:
    def __init__(self):
        self.sigid = None
        self.trig_dbs = []
        self.trig_count = 0

        # called result entries
        self.player_result_entries = []
        self.force_players = [set(), set(), set(), set()]
        for pid in range(8):
            self.force_players[GetPlayerInfo(pid).force].add(pid)

        # total result tables
        self.result_tables = []

        # connect function to use inline eudplib
        EUDRegisterObjectToNamespace("screpl_condcheck", self.condcheck_inline)

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

        trig_object = Db(trigger)

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
            mcb = MaximumCircularBuffer(ResultEntry).construct_w_empty([
                ResultEntry.construct() for _ in range(ENTRY_SIZE)
            ])
            result_entries[pid] = mcb
            self.result_tables.append((trig_object,
                                       len(self.trig_dbs),
                                       pid,
                                       mcb))

        # construct inline trigger
        inline_trig = (bytes(20)
                       + i2b4(0x10978d4a)
                       + i2b4(player_code)
                       + ('screpl_condcheck(%d, f_getcurpl())'
                          % self.trig_count).encode())
        inline_trig += bytes(2400-len(inline_trig))

        self.trig_count += 1
        self.trig_dbs.append(trig_object)
        self.player_result_entries.append(result_entries)

        return inline_trig

    def condcheck_inline(self, trig_id, player_id):
        trig_db = self.trig_dbs[trig_id]
        player_result_entry = self.player_result_entries[trig_id]
        EUDSwitch(player_id)
        result_entry = EUDVariable()
        for entry_player_id, entry in player_result_entry.items():
            EUDSwitchCase()(entry_player_id)
            result_entry << entry
            EUDBreak()
        if EUDSwitchDefault()():
            f_raise_error("screpl-condcheck trig id %D - player id %D unknown",
                          trig_id, player_id)
        EUDEndSwitch()
        _condcheck_trigger(EPD(trig_db), result_entry)

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
                if string == b'screpl-condcheck':
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

cctm = CondCheckTriggerManager()

def plugin_setup():
    cctm.find_signature_and_update()

    if cctm.trig_count:
        from .condcheck import CondCheckApp

        @AppCommand([])
        def start_condcheck(self):
            app_manager.start_application(CondCheckApp)

        REPL.add_command('condcheck', start_condcheck)
