from eudplib import *
from ..apps.logger import Logger

class ProfileTable:
    '''
    Class required by communication between bridge client
    '''
    def __init__(self):
        self.table = []

    def append(self, name, total, counter):
        '''
        name   : variable name
        total  : total milliseconds
        counter: monitored counter
        '''
        self.table.append((name, total, counter))

    def getSize(self):
        return len(self.table)

profile_table = ProfileTable()

def REPLMonitorPush(name, logger_log = True):
    if logger_log:
        Logger.format("[{}] <--".format(name))

    v_start = f_getInversedTickCount()
    v_total, v_count = EUDCreateVariables(2)
    profile_table.append(name, v_total, v_count)

    EUDCreateBlock("replmonitorblock", {
        'name': name,
        'start': v_start,
        'total': v_total,
        'count': v_count,
        'logger_log': logger_log
    })

def REPLMonitorPop():
    bname, userdata = EUDPopBlock("replmonitorblock")

    v_end = f_getInversedTickCount()
    name = userdata['name']
    v_start = userdata['start']
    v_total = userdata['total']
    v_count = userdata['count']
    logger_log = userdata['logger_log']

    # v_start -= v_end
    # v_total += v_start
    SeqCompute([
        (v_count, Add, 1),
        (v_start, Subtract, v_end),
        (v_total, Add, v_start),
    ])

    if logger_log:
        Logger.format("[{}] --> %D ms".format(name), v_start)

@EUDFunc
def f_getInversedTickCount():
    countdownTimer = f_dwread_epd(EPD(0x57F0F0 + 0xe604))
    elapsedTime    = f_dwread_epd(EPD(0x57F0F0 + 0xe608))
    triggerTimer   = f_dwread_epd(EPD(0x6509A0))
    DoActions(SetMemory(0x6509A0, SetTo, 0))
    EUDDoEvents()

    # restore timers
    SeqCompute([
        (EPD(0x57F0F0 + 0xe604), SetTo, countdownTimer),
        (EPD(0x57F0F0 + 0xe608), SetTo, elapsedTime),
        (EPD(0x6509A0), SetTo, triggerTimer),
    ])
    EUDReturn(f_dwread_epd(EPD(0x51CE8C)))
