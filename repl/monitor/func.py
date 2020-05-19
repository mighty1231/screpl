from eudplib import *
from . import profile_table, f_getInversedTickCount

def REPLMonitorF(io=True, profile=True):
    def monitor(func):
        if isinstance(func, EUDFuncN):
            return REPLMonitorEUDFunc(func, io, profile)
        elif isinstance(func, _AppMethod):
            return REPLMonitorAppMethod(func, io, profile)
        elif isinstance(func, _AppCommand):
            return REPLMonitorAppCommand(func, io, profile)
        raise RuntimeError(
            "Currently REPLMonitor supports EUDFuncN, AppCommand, and AppMethod"
        )

    return monitor

def REPLEUDFunc(funcn, io=True, profile=False):
    pass

def REPLMonitorAppMethod(funcn, io=True, profile=False):
    pass

def REPLMonitorAppCommand(funcn, io=True, profile=False):
    pass
