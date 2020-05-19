from eudplib import *
from ..apps.logger import Logger
from . import profile_table, f_getInversedTickCount

def REPLMonitorPush(name, profile = True, log = True):
    blockdata = {
        'name': name,
        'profile': profile,
        'log': log,
    }

    if log:
        Logger.format("[{}] <--".format(name))

    if profile:
        v_start = f_getInversedTickCount()
        v_total, v_count = EUDCreateVariables(2)
        profile_table.append(name, v_total, v_count)
        blockdata['start'] = v_start
        blockdata['total'] = v_total
        blockdata['count'] = v_count

    EUDCreateBlock("replmonitorblock", blockdata)

def REPLMonitorPop():
    bname, blockdata = EUDPopBlock("replmonitorblock")

    name = blockdata['name']
    profile = blockdata['profile']
    log = blockdata['log']

    if profile:
        v_start = blockdata['start']
        v_total = blockdata['total']
        v_count = blockdata['count']

        v_end = f_getInversedTickCount()

        # v_start -= v_end
        # v_total += v_start
        SeqCompute([
            (v_count, Add, 1),
            (v_start, Subtract, v_end),
            (v_total, Add, v_start),
        ])

    if log:
        if profile:
            Logger.format("[{}] --> %D ms".format(name), v_start)
        else:
            Logger.format("[{}] -->".format(name))
