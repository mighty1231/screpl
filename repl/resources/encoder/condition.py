from eudplib import *

def encodeCondition_epd(condition_epd, cond):
    '''
     ======  =============  ========  ===========
     Offset  Field Name     Position  EPD Player
     ======  =============  ========  ===========
       +00   locid           dword0   EPD(cond)+0
       +04   player          dword1   EPD(cond)+1
       +08   amount          dword2   EPD(cond)+2
       +0C   unitid          dword3   EPD(cond)+3
       +0E   comparison
       +0F   condtype
       +10   restype         dword4   EPD(cond)+4
       +11   flags
       +12   internal[2]
     ======  =============  ========  ===========
    '''
    assert isinstance(cond, Condition)

    f_dwwrite_epd(action_epd + 4, 0)

    if type(act.fields[0]) != int or act.fields[0] != 0:
        f_dwwrite_epd(action_epd, act.fields[0])
    if type(act.fields[1]) != int or act.fields[1] != 0:
        f_dwwrite_epd(action_epd + 1, act.fields[1])
    if type(act.fields[2]) != int or act.fields[2] != 0:
        f_dwwrite_epd(action_epd + 2, act.fields[2])
    if type(act.fields[3]) != int or act.fields[3] != 0:
        f_wwrite_epd(action_epd + 3, 0, act.fields[3])
    if type(act.fields[4]) != int or act.fields[4] != 0:
        f_bwrite_epd(action_epd + 3, 2, act.fields[4])
    if type(act.fields[5]) != int or act.fields[5] != 0:
        f_bwrite_epd(action_epd + 3, 3, act.fields[5])
    if type(act.fields[6]) != int or act.fields[6] != 0:
        f_bwrite_epd(action_epd + 4, 0, act.fields[6])
    if type(act.fields[7]) != int or act.fields[7] != 0:
        f_bwrite_epd(action_epd + 4, 1, act.fields[7])
    if type(act.fields[8]) != int or act.fields[8] != 0:
        f_wwrite_epd(action_epd + 4, 2, act.fields[8])
