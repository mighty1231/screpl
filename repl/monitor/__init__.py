from eudplib import *

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
