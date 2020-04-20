from eudplib import *

@EUDFunc
def f_strcmp_ptrepd(s1, s2):
    EUDReturn(f_strcmp(s1, (s2 * 4) + 0x58A364))
