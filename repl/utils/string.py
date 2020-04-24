from eudplib import *

@EUDFunc
def f_strcmp_ptrepd(s1, s2):
    EUDReturn(f_strcmp(s1, (s2 * 4) + 0x58A364))

@EUDFunc
def f_strlen(s):
    from ..base.eudbyterw import EUDByteRW
    reader = EUDByteRW()
    cnt = EUDVariable()

    reader.seekoffset(s)
    cnt << 0
    if EUDInfLoop()():
        ch = reader.read()
        EUDBreakIf(ch == 0)
        DoActions(cnt.AddNumber(1))
    EUDEndInfLoop()
    EUDReturn(cnt)
