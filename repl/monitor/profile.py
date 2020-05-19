from eudplib import *
from ..apps.logger import Logger
from . import profile_table, f_getInversedMillis, f_getGameSpeed

def REPLMonitorPush(name, profile=True, log=True):
    blockdata = {
        'name': name,
        'profile': profile,
        'log': log,
    }

    if log:
        Logger.format("<{}> entered".format(name))

    if profile:
        v_count = EUDVariable()
        v_startMillis = f_getInversedMillis()
        v_totalMillis = EUDVariable()
        v_startTick = f_getgametick()
        v_totalExpected = EUDVariable()
        profile_table.append(name, v_count, v_totalMillis, v_totalExpected)
        blockdata['count'] = v_count
        blockdata['start-m'] = v_startMillis
        blockdata['total-m'] = v_totalMillis
        blockdata['start-t'] = v_startTick
        blockdata['total-e'] = v_totalExpected

    EUDCreateBlock("replmonitorblock", blockdata)

    return True # enables "if REPLMonitorPush():"

def REPLMonitorPop():
    bname, blockdata = EUDPopBlock("replmonitorblock")

    name = blockdata['name']
    profile = blockdata['profile']
    log = blockdata['log']

    if profile:
        v_count = blockdata['count']
        v_startMillis = blockdata['start-m']
        v_totalMillis = blockdata['total-m']
        v_startTick = blockdata['start-t']
        v_totalExpected = blockdata['total-e']

        v_endMillis = f_getInversedMillis()
        v_endTick = f_getgametick()

        # v_startMillis -= v_endMillis
        # v_totalMillis += v_startMillis
        # v_endTick -= v_startTick
        # ==> v_startMillis: millis diff
        #     v_endTick: tick diff
        SeqCompute([
            (v_count, Add, 1),
            (v_startMillis, Subtract, v_endMillis),
            (v_totalMillis, Add, v_startMillis),
            (v_endTick, Subtract, v_startTick)
        ])
        v_additionalExpected = v_endTick * f_getGameSpeed()
        v_totalExpected += v_additionalExpected

    if log:
        if profile:
            Logger.format("<{}> exited, %D ms (Expected %D)".format(name),
                v_startMillis,
                v_additionalExpected
            )
            return v_startMillis, v_additionalExpected
        else:
            Logger.format("<{}> exited".format(name))

    if profile:
        # consumed_ms, expected_ms
        return v_startMillis, v_additionalExpected
