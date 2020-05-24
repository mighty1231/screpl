from eudplib import *

def encode_condition_epd(condition_epd, cond):
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

    f_dwwrite_epd(condition_epd + 4, 0)

    if not isinstance(cond.fields[0], int) or cond.fields[0] != 0:
        f_dwwrite_epd(condition_epd, cond.fields[0])
    if not isinstance(cond.fields[1], int) or cond.fields[1] != 0:
        f_dwwrite_epd(condition_epd + 1, cond.fields[1])
    if not isinstance(cond.fields[2], int) or cond.fields[2] != 0:
        f_dwwrite_epd(condition_epd + 2, cond.fields[2])
    if not isinstance(cond.fields[3], int) or cond.fields[3] != 0:
        f_wwrite_epd(condition_epd + 3, 0, cond.fields[3])
    if not isinstance(cond.fields[4], int) or cond.fields[4] != 0:
        f_bwrite_epd(condition_epd + 3, 2, cond.fields[4])
    if not isinstance(cond.fields[5], int) or cond.fields[5] != 0:
        f_bwrite_epd(condition_epd + 3, 3, cond.fields[5])
    if not isinstance(cond.fields[6], int) or cond.fields[6] != 0:
        f_bwrite_epd(condition_epd + 4, 0, cond.fields[6])
    if not isinstance(cond.fields[7], int) or cond.fields[7] != 0:
        f_bwrite_epd(condition_epd + 4, 1, cond.fields[7])
    if not isinstance(cond.fields[8], int) or cond.fields[8] != 0:
        f_wwrite_epd(condition_epd + 4, 2, cond.fields[8])
