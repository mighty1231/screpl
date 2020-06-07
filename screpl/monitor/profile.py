from eudplib import *

from screpl.apps.logger import Logger
from . import profile_table, f_get_inversed_millis, f_get_gamespeed

def repl_monitor_push(name, profile=True, log=True):
    blockdata = {
        'name': name,
        'profile': profile,
        'log': log,
    }

    if log:
        Logger.format("<{}> entered".format(name))

    if profile:
        v_count = EUDVariable()
        v_start_millis = f_get_inversed_millis()
        v_total_millis = EUDVariable()
        v_start_tick = f_getgametick()
        v_total_expected = EUDVariable()
        profile_table.append(name, v_count, v_total_millis, v_total_expected)
        blockdata['count'] = v_count
        blockdata['start-m'] = v_start_millis
        blockdata['total-m'] = v_total_millis
        blockdata['start-t'] = v_start_tick
        blockdata['total-e'] = v_total_expected

    EUDCreateBlock("replmonitorblock", blockdata)

    return True # enables "if REPLMonitorPush():"

def repl_monitor_pop():
    _, blockdata = EUDPopBlock("replmonitorblock")

    name = blockdata['name']
    profile = blockdata['profile']
    log = blockdata['log']

    if profile:
        v_count = blockdata['count']
        v_start_millis = blockdata['start-m']
        v_total_millis = blockdata['total-m']
        v_start_tick = blockdata['start-t']
        v_total_expected = blockdata['total-e']

        v_end_millis = f_get_inversed_millis()
        v_end_tick = f_getgametick()

        # v_start_millis -= v_end_millis
        # v_total_millis += v_start_millis
        # v_end_tick -= v_start_tick
        # ==> v_start_millis: millis diff
        #     v_end_tick: tick diff
        SeqCompute([
            (v_count, Add, 1),
            (v_start_millis, Subtract, v_end_millis),
            (v_total_millis, Add, v_start_millis),
            (v_end_tick, Subtract, v_start_tick)
        ])
        v_additional_expected = v_end_tick * f_get_gamespeed()
        v_total_expected += v_additional_expected

    if log:
        if profile:
            Logger.format("<{}> exited, %D ms (Expected %D)".format(name),
                          v_start_millis,
                          v_additional_expected)
            return v_start_millis, v_additional_expected
        else:
            Logger.format("<{}> exited".format(name))

    if profile:
        # consumed_ms, expected_ms
        return v_start_millis, v_additional_expected
