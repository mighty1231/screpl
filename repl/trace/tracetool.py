from eudplib import *
from ..apps.logger import Logger

class TraceLog:
    '''
    Object required by communication between bridge client
    '''
    def __init__(self):
        self.trace_vars = []

    def append(self, name, total, count):
        self.trace_vars.append((name, total, count))

tracelog = TraceLog()

def REPLTracePush(name, logger_log = True):
    if logger_log:
        Logger.format("[{}] <--".format(name))

    v_start = f_dwread_epd(EPD(0x51CE8C)) # inversed tickcount
    v_total, v_count = EUDCreateVariables(2)
    tracelog.append(name, v_total, v_count)

    EUDCreateBlock("repltraceblock", {
        'start': v_start,
        'total': v_total,
        'count': v_count,
        'logger_log': logger_log
    })

def REPLTracePop():
    name, userdata = EUDPopBlock("repltraceblock")

    v_end = f_dwread_epd(EPD(0x51CE8C)) # inversed tickcount
    v_start = userdata['start']
    v_total = userdata['total']
    v_count = userdata['count']
    logger_log = userdata['logger_log']

    # v_start -= v_end
    # v_total += v_start
    SeqCompute([
        (v_count, Add, 1)
        (v_start, Subtract, v_end),
        (v_total, Add, v_start),
    ])

    if logger_log:
        Logger.format("[{}] --> %D ms".format(name), v_start)
