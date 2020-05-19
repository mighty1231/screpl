from eudplib import *

class ProfileTable:
    '''
    Class required by communication between bridge client
    '''
    def __init__(self):
        self.table = []

    def append(self, name, counter, totalMillis, totalExpectedMillis):
        '''
        name        : variable name
        counter     : monitored counter
        totalMillis : total milliseconds
        totalExpectedMillis : total expected milliseconds
        '''
        self.table.append((name, counter, totalMillis, totalExpectedMillis))

    def getSize(self):
        return len(self.table)

profile_table = ProfileTable()

@EUDFunc
def f_getInversedMillis():
    '''
    0x51CE8C: inversed tick count. 1 for 1 ms
     * Since it is not updated during trigger execution,
       EUDDoEvents should be called
    '''
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

@EUDFunc
def f_getGameSpeed():
    '''
    0x5124F0 : GameSpeedModifier
     - count of milliseconds per a single gametick
    '''
    speed = EUDVariable()
    if EUDIfNot()(Memory(0x5124F0, Exactly, speed)):
        speed << f_dwread_epd(EPD(0x5124F0))
    EUDEndIf()
    EUDReturn(speed)
