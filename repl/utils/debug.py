from eudplib import *

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
