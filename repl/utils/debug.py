from eudplib import *

_buf = Db(2048)

def f_raiseError(txt):
    f_setcurpl(f_getuserplayerid())
    DoActions([
        DisplayText(txt),
        SetMemory(0, Add, 1),
    ])

def f_raiseWarning(txt):
    f_setcurpl(f_getuserplayerid())
    DoActions([
        DisplayText(txt),
    ])

def print_f(*args):
    from ..base.eudbyterw import EUDByteRW

    if EUDExecuteOnce()():
        STRSection, STRSection_epd = f_dwepdread_epd(EPD(0x5993D4))
    EUDEndExecuteOnce()

    writer = EUDByteRW()
    writer.seekepd(EPD(_buf))
    writer.write_f(*args)
    writer.write(0)
    orig_cp = f_getcurpl()
    f_setcurpl(f_getuserplayerid())

    prev_offset = f_dwread_epd(STRSection_epd + 1)
    DoActions([
        SetMemoryEPD(STRSection_epd + 1, SetTo, _buf - STRSection),
        DisplayText(1),
        SetMemoryEPD(STRSection_epd + 1, SetTo, prev_offset)
    ])

    f_setcurpl(orig_cp)
