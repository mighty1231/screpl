from eudplib import (
    Add,
    DoActions,
    EPD,
    EUDBreakIf,
    EUDEndIf,
    EUDEndInfLoop,
    EUDEndWhile,
    EUDFunc,
    EUDIfNot,
    EUDInfLoop,
    EUDReturn,
    EUDWhileNot,
    EUDVariable,
    Exactly,
    Forward,
    f_dwread_cp,
    f_strcmp,
    f_setcurpl2cpcache,
    Memory,
    SetTo,
    SetMemory,
    SeqCompute,
    VProc,
)
from . import byterw

@EUDFunc
def f_strcmp_ptrepd(s1, s2):
    EUDReturn(f_strcmp(s1, (s2 * 4) + 0x58A364))

@EUDFunc
def f_strlen(s):
    reader = byterw.REPLByteRW()
    cnt = EUDVariable()

    reader.seekoffset(s)
    cnt << 0
    if EUDInfLoop()():
        ch = reader.read()
        EUDBreakIf(ch == 0)
        DoActions(cnt.AddNumber(1))
    EUDEndInfLoop()
    EUDReturn(cnt)

@EUDFunc
def f_memcmp_epd(epd1, epd2, cnt):
    """If same, return 0"""
    comp = Forward()

    VProc([epd1, epd2], [
        epd1.SetDest(EPD(comp+4)),
        epd2.SetDest(EPD(0x6509B0)),
    ])

    if EUDWhileNot()(cnt == 0):
        value = f_dwread_cp(0)
        SeqCompute([(EPD(comp+8), SetTo, value)])

        # *epd1 == *epd2
        if EUDIfNot()(comp << Memory(0, Exactly, 0)):
            f_setcurpl2cpcache()
            EUDReturn(1)
        EUDEndIf()

        DoActions([
            SetMemory(comp+4, Add, 1),
            SetMemory(0x6509B0, Add, 1),
            cnt.SubtractNumber(1),
        ])
    EUDEndWhile()

    f_setcurpl2cpcache()
    EUDReturn(0)
