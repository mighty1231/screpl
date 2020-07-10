"""

Calling another coroutine inside coroutine

unity C#

yeild return must be inside IEnumerator

yield return null; // wait 1 frame
yield return new WaitForSecond(float time);
yield return new WaitForSecondRealtime(float time)
// yield return new WaitForEndOfFrame()
yield return new WaitUntil(system.Func<Bool> predicate);
yield return new WaitWhile(system.Func<Bool> predicate);
yield return StartCoroutine(IEnumerator coroutine); // synchronously

public void StartCoroutine(IEnumerator routine);
public void StopCoroutine(IEnumerator routine);
public void StopCoroutine(string methodName);
public void StopAllCoroutine();

every start -> create context...

# safety!
coroutine with same context should not be executed at a moment
but reusable!

all coroutines = []


"""
import inspect
import sys

from eudplib import *

from .struct import REPLStruct
from .array import create_refarray, REPLArray

"""Unique coroutine manager"""
_manager = None

def get_coroutine_manager():
    """Returns unique CoroutineManager instance"""
    global _manager
    if not _manager:
        _manager = CoroutineManager()
    return _manager

class PyCoroutine:
    """Simple object to describe Coroutine object"""
    def __init__(self, id_, trig_start, trig_end):
        self.id = id_
        self.trig_start = trig_start
        self.trig_end = trig_end
        self.used = EUDVariable(0)

    def switch_on(self):
        """Assert single PyCoroutine object cannot be started twice"""
        f_assert(self.used == 0, "Context of coroutine is already used")
        self.used << 1

    def switch_off(self):
        self.used << 0

class Coroutine(REPLStruct):
    fields = [
        'id',
        'trig_next',

        # wait frames
        'tick_next',

        # coroutine context usage status
        'trig_end',
    ]

    @classmethod
    def empty(self):
        return Coroutine.initialize_with(0, 0, 0, 0, 0)

    @classmethod
    def args(cls, *args, **kwargs):
        """Create coroutine object"""
        cm = get_coroutine_manager()
        trig_start, trig_end, trig_jumper = Forward(), Forward(), Forward()
        pycoroutine = cm.create_pycoroutine(trig_start, trig_end, trig_jumper)

        f_bsm = BlockStruManager()
        prev_bsm = SetCurrentBlockStruManager(f_bsm)
        PushTriggerScope()
        trig_start << NextTrigger()

        # make pycoroutine safe
        pycoroutine.switch_on()

        cur_coroutine_instance = cm.get_current_coroutine()
        cls.run(cur_coroutine_instance, *args, **kwargs)

        # make clear
        trig_end << NextTrigger() # used on StopCoroutine
        pycoroutine.switch_off()

        # end of coroutine
        # remove current coroutine
        if EUDIf()(coroutine.id == pycoroutine.id):
            # not applied for coroutine inside other coroutine
            # let coroutine manager know the end of coroutine
            coroutine.trig_next = 0
        EUDEndIf()

        trig_jumper << RawTrigger(
            nextptr=get_coroutine_manager().coroutine_end)

        PopTriggerScope()
        assert f_bsm.empty(), 'Block start/end mismatch inside coroutine'
        SetCurrentBlockStruManager(prev_bsm)

        return coroutine

    def run(self, *args, **kwargs):
        """Main part of coroutine, should be overrided

        Every coroutine instance creates full context for run()
        """
        raise NotImplementedError

    def wait_for_frame(self, cnt):
        """Stop coroutine, waiting for CNT frames

        if cnt is 0, current run is not be yielded
        """
        tick = get_coroutine_manager().tick
        trig_next = Forward()
        self.tick_next = tick + cnt
        self.trig_next = trig_next
        EUDJumpIfNot(cnt == 0, get_coroutine_manager().coroutine_end)
        trig_next << NextTrigger()

    def wait1(self):
        """Wait a single frame"""
        self.wait_for_frame(1)

    def wait_for_second(self, sec):
        """Stop coroutine, waiting for SEC seconds

        note: StarCraft has 24 FPS
        """
        self.wait_for_frame(sec // 24)

    def wait_until(self, conditions):
        """Stop coroutine, wait for condition become true"""
        trig_check = NextTrigger()
        if EUDIfNot()(conditions):
            self.trig_next = trig_check
            EUDJump(get_coroutine_manager().coroutine_end)
        EUDEndIf()

    def wait_while(self, conditions):
        """Stop coroutine, wait for condition become false"""
        trig_check = NextTrigger()
        if EUDIf()(conditions):
            self.trig_next = trig_check
            EUDJump(get_coroutine_manager().coroutine_end)
        EUDEndIf()

    def start_coroutine(self, coroutine):
        """Start another coroutine"""
        assert isinstance(coroutine, PyCoroutine)
        trig_next = Forward()
        f_dwwrite_epd(EPD(coroutine.trig_jumper + 4), trig_next)
        EUDJump(coroutine.trig_start)
        trig_next << NextTrigger()
        f_dwwrite_epd(EPD(coroutine.trig_jumper + 4),
                      get_coroutine_manager().coroutine_end)


CoroutineArray = create_refarray(Coroutine, Coroutine.empty)

class CoroutineManager:
    def __init__(self):
        self.pycoroutines = []
        self.active_coroutines = CoroutineArray(200)
        self.coroutine_end = Forward()
        self.cid = 0
        self.tick = EUDVariable()

        self.cur_coroutine = Coroutine.empty_pointer() # EUDVariable

    def get_current_coroutine(self):
        return self.cur_coroutine

    def create_pycoroutine(self, trig_start, trig_end):
        self.cid += 1
        pycoroutine = PyCoroutine(self.cid, trig_start, trig_end)
        self.pycoroutines.append(pycoroutine)

    def start_coroutine(self, pycoroutine):
        """Add alive coroutine object"""
        assert isinstance(pycoroutine, PyCoroutine)

        coroutine = self.active_coroutines.push_and_getref()
        coroutine.id = pycoroutine.id
        coroutine.trig_next = pycoroutine.trig_start
        coroutine.tick_next = 0
        coroutine.trig_end = pycoroutine.trig_end

    def stop_coroutine(self, pycoroutine):
        assert isinstance(pycoroutine, PyCoroutine)
        self._stop_coroutine(pycoroutine.id)

    @EUDMethod
    def _stop_coroutine(self, coroutine_id):
        """Iterate coroutines, find target with id and remove it"""
        idx, found = EUDCreateVariable(2)
        DoActions([idx.SetNumber(0), found.SetNumber(0)])

        for coroutine in self.active_coroutines.values():
            if EUDIf()(coroutine.id == coroutine_id):
                found << 1
                coroutine.tick_next = 0
                coroutine.trig_next = coroutine.trig_end
                EUDBreak()
            EUDEndIf()
            idx += 1

        # f_assert(found, "coroutine id=%D is not found", coroutine_id)

    def update(self):
        idx = EUDVariable()
        self.tick << f_getgametick()
        idx << 0
        idxes_to_remove = REPLArray(200)
        for coroutine in self.active_coroutines.values():
            # set current coroutine
            self.cur_coroutine << coroutine

            """Continue coroutine"""
            if EUDIf()(self.cur_coroutine.tick_next <= self.tick):
                EUDJump(self.cur_coroutine.trig_next)
            EUDEndIf()

            self.coroutine_end << NextTrigger()

            if EUDIf()(coroutine.trig_next == 0):
                idxes_to_remove.append(idx)
            if EUDElse()():
                idx += 1
            EUDEndIf()

        # clear completed coroutines
        for idx in idxes_to_remove.values():
            self.active_coroutines.delete(idx)
        idxes_to_remove.clear()
