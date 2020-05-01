from eudplib import *

def encodeAction_epd(action_epd, act):
    '''
     ======  ============= ========  ==========
     Offset  Field Name    Position  EPD Player
     ======  ============= ========  ==========
       +00   locid1         dword0   EPD(act)+0
       +04   strid          dword1   EPD(act)+1
       +08   wavid          dword2   EPD(act)+2
       +0C   time           dword3   EPD(act)+3
       +10   player1        dword4   EPD(act)+4
       +14   player2        dword5   EPD(act)+5
       +18   unitid         dword6   EPD(act)+6
       +1A   acttype
       +1B   amount
       +1C   flags          dword7   EPD(act)+7
       +1D   internal[3
     ======  ============= ========  ==========
    '''
    assert isinstance(act, Action)

    f_dwwrite_epd(action_epd + 7, 0)

    if type(act.fields[0]) != int or act.fields[0] != 0:
        f_dwwrite_epd(action_epd, act.fields[0])
    if type(act.fields[1]) != int or act.fields[1] != 0:
        f_dwwrite_epd(action_epd + 1, act.fields[1])
    if type(act.fields[2]) != int or act.fields[2] != 0:
        f_dwwrite_epd(action_epd + 2, act.fields[2])
    if type(act.fields[3]) != int or act.fields[3] != 0:
        f_dwwrite_epd(action_epd + 3, act.fields[3])
    if type(act.fields[4]) != int or act.fields[4] != 0:
        f_dwwrite_epd(action_epd + 4, act.fields[4])
    if type(act.fields[5]) != int or act.fields[5] != 0:
        f_dwwrite_epd(action_epd + 5, act.fields[5])
    if type(act.fields[6]) != int or act.fields[6] != 0:
        f_wwrite_epd(action_epd + 6, 0, act.fields[6])
    if type(act.fields[7]) != int or act.fields[7] != 0:
        f_bwrite_epd(action_epd + 6, 2, act.fields[7])
    if type(act.fields[8]) != int or act.fields[8] != 0:
        f_bwrite_epd(action_epd + 6, 3, act.fields[8])
    if type(act.fields[9]) != int or act.fields[9] != 0:
        f_bwrite_epd(action_epd + 7, 0, act.fields[9])
    if type(act.fields[11]) != int or act.fields[11] != 0:
        f_write_epd(action_epd + 7, 2, act.fields[11])
