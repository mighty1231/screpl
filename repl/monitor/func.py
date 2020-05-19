from eudplib import *

from ..apps import Logger
from ..core.application import ApplicationInstance
from ..core.appmethod import _AppMethod
from ..core.appcommand import _AppCommand
from . import profile_table, f_getInversedTickCount

import inspect

def REPLMonitorF(io=True, profile=True):
    '''
    Decorator function to monitor function-classes
    '''
    def monitor(func):
        if isinstance(func, EUDFuncN):
            return REPLMonitorEUDFunc(func, io, profile)
        elif isinstance(func, _AppMethod):
            REPLMonitorAppMethod(func, io, profile)
            return func
        elif isinstance(func, _AppCommand):
            REPLMonitorAppCommand(func, io, profile)
            return func
        raise RuntimeError(
            "Currently REPLMonitor supports EUDFuncN, AppCommand, and AppMethod"
        )

    return monitor

monitored_objects = []

def REPLMonitorEUDFunc(funcn, io=True, profile=False):
    assert funcn not in monitored_objects, "func should not be monitored twice"

    if funcn._fstart:
        raise RuntimeError("EUDFuncN already constructed")

    old_caller = funcn._callerfunc
    def new_caller(*args):
        _inputs = [EUDVariable() for _ in range(funcn._argn)]
        for i, v in zip(_inputs, args):
            i << v

        final_rets = old_caller(*args)

        if final_rets is not None:
            funcn._AddReturn(Assignable2List(final_rets), False)
        funcn._fend << NextTrigger() # To catch EUDReturn

        if funcn._retn is None:
            _outputs = []
        else:
            _outputs = [EUDVariable() for _ in range(funcn._retn)]
            for i, v in zip(_outputs, funcn._frets):
                i << v

        # Log format: my_function(arg1=3, arg2=4) -> (2, 4)
        # EUDFuncN / AppMethod both case have their arguments at last
        if funcn._argn:
            argnames = inspect.getfullargspec(funcn._bodyfunc).args[-funcn._argn:]
        else:
            argnames = []
        fmtstring = "{}({}) -> ".format(
            funcn._bodyfunc.__qualname__,
            ", ".join(["{}=%D".format(name) for name in argnames]),
        )
        if len(_outputs) == 0:
            fmtstring += "."
        elif len(_outputs) == 1:
            fmtstring += "%D"
        else:
            fmtstring += ", ".join(["%D"] * len(_outputs))
        Logger.format(fmtstring, *(_inputs + _outputs))

        funcn._fend = Forward()
        return None
    funcn._callerfunc = new_caller
    monitored_objects.append(funcn)

    return funcn

def REPLMonitorAppMethod(appmtd, io=True, profile=False):
    appmtd.setFuncnCallback(REPLMonitorEUDFunc)

def REPLMonitorAppCommand(appcmd, io=True, profile=False):
    assert appcmd not in monitored_objects, "command should not be monitored twice"

    def cb(old_func):
        def new_func(self, *args):
            assert isinstance(self, ApplicationInstance)
            _inputs = [EUDVariable() for _ in range(appcmd.argn)]
            for i, v in zip(_inputs, args):
                i << v

            # Log format: my_app.my_cmd(arg1=3, arg2=4)
            argnames = inspect.getfullargspec(old_func).args[1:]
            fmtstring = "{}({})".format(
                old_func.__qualname__,
                ", ".join(["{}=%D".format(name) for name in argnames])
            )
            Logger.format(fmtstring, *_inputs)

            return old_func(self, *args)
        return new_func
    appcmd.setFuncCallback(cb)
