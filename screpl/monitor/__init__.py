from eudplib import *

class ProfileTable:
    '''
    Class required by communication between bridge client
    '''
    def __init__(self):
        self.table = []

    def append(self, name, counter, total_millis, total_expected_millis):
        '''
        name        : variable name
        counter     : monitored counter
        total_millis : total milliseconds
        total_expected_millis : total expected milliseconds
        '''
        self.table.append((name, counter, total_millis, total_expected_millis))

    def get_size(self):
        return len(self.table)

profile_table = ProfileTable()

@EUDFunc
def f_get_inversed_millis():
    '''
    0x51CE8C: inversed tick count. 1 for 1 ms
     * Since it is not updated during trigger execution,
       EUDDoEvents should be called
    '''
    v_countdown_timer = f_dwread_epd(EPD(0x57F0F0 + 0xe604))
    v_elapsed_time = f_dwread_epd(EPD(0x57F0F0 + 0xe608))
    v_trigger_timer = f_dwread_epd(EPD(0x6509A0))
    DoActions(SetMemory(0x6509A0, SetTo, 0))
    EUDDoEvents()

    # restore timers
    SeqCompute([
        (EPD(0x57F0F0 + 0xe604), SetTo, v_countdown_timer),
        (EPD(0x57F0F0 + 0xe608), SetTo, v_elapsed_time),
        (EPD(0x6509A0), SetTo, v_trigger_timer),
    ])
    EUDReturn(f_dwread_epd(EPD(0x51CE8C)))

@EUDFunc
def f_get_gamespeed():
    '''
    0x5124F0 : GameSpeedModifier
     - count of milliseconds per a single gametick
    '''
    speed = EUDVariable()
    if EUDIfNot()(Memory(0x5124F0, Exactly, speed)):
        speed << f_dwread_epd(EPD(0x5124F0))
    EUDEndIf()
    EUDReturn(speed)
