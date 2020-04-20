from eudplib import *

def f_raiseError(txt):
    DoActions([
        SetCurrentPlayer(f_getuserplayerid()),
        DisplayText(txt),
        SetMemory(0, Add, 1),
    ])

def f_raiseWarning(txt):
    DoActions([
        SetCurrentPlayer(f_getuserplayerid()),
        DisplayText(txt),
    ])
