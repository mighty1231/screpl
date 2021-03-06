import inspect
import functools

from eudplib import *

from screpl.apps.logger import Logger
from screpl.core.application import ApplicationInstance
from screpl.core.appmethod import AppMethodN
from screpl.core.appcommand import AppCommandN
from .profile import repl_monitor_push
from .profile import repl_monitor_pop


def repl_monitor_f(io=True, profile=True):
    '''
    Decorator function to monitor function-classes
    '''
    def monitor(func):
        if isinstance(func, EUDFuncN):
            return repl_monitor_eudfunc(func, io, profile)
        elif isinstance(func, AppMethodN):
            repl_monitor_appmethod(func, io, profile)
            return func
        elif isinstance(func, AppCommandN):
            repl_monitor_appcommand(func, io, profile)
            return func
        raise RuntimeError(
            "Currently repl_monitor_f supports EUDFuncN, AppCommand, and AppMethod"
        )

    return monitor

monitored_objects = []

def repl_monitor_eudfunc(funcn, io=True, profile=False):
    # pylint: disable=protected-access
    assert funcn not in monitored_objects, "func should not be monitored twice"

    if funcn._fstart:
        raise RuntimeError("EUDFuncN already constructed")

    old_caller = funcn._callerfunc
    def new_caller(*args):
        func_name = funcn._bodyfunc.__qualname__

        # log input
        if io and funcn._argn:
            # Log format: <func_name:arg1=3, arg2=4> entered
            # EUDFuncN / AppMethod both case have their arguments at last
            argnames = inspect.getfullargspec(funcn._bodyfunc).args[-funcn._argn:]
            Logger.format("<{}/{}> entered".format(
                func_name,
                ", ".join(["{}=%D".format(name) for name in argnames])
            ), *args)
        else:
            Logger.format("<{}> entered".format(func_name))

        if profile:
            repl_monitor_push(func_name, profile=True, log=False)

        # call original caller
        final_rets = old_caller(*args)

        # intercept outputs
        if final_rets is not None:
            funcn._AddReturn(Assignable2List(final_rets), False)
        funcn._fend << NextTrigger() # To catch EUDReturn

        if profile:
            tickdiff, expected = repl_monitor_pop()

        # build log
        if funcn._retn:
            outputs = funcn._frets
        else:
            outputs = []

        fmtstring = "<{}> exited".format(func_name)
        args = []

        if io:
            fmtstring = fmtstring.replace("exited", "returned")
            fmtstring += " ({})".format(", ".join(["%D"] * len(outputs)))
            args += outputs
        if profile:
            fmtstring += ", %D ms (Expected %D)"
            args += [tickdiff, expected]

        Logger.format(fmtstring, *args)

        funcn._fend = Forward()
        return None
    funcn._callerfunc = new_caller
    monitored_objects.append(funcn)

    return funcn

def repl_monitor_appmethod(appmtd, io=True, profile=False):
    appmtd.set_funcn_callback(
        functools.partial(repl_monitor_eudfunc,
                          io=io, profile=profile))

def repl_monitor_appcommand(appcmd, io=True, profile=False):
    assert appcmd not in monitored_objects, "command should not be monitored twice"

    def cb(old_func):
        def new_func(self, *args):
            assert isinstance(self, ApplicationInstance)

            func_name = old_func.__qualname__

            # log input
            if io and len(args) > 0:
                # Log format: <app.cmdname:arg1=3, arg2=4> entered
                # EUDFuncN / AppMethod both case have their arguments at last
                argnames = inspect.getfullargspec(old_func).args[1:]
                Logger.format("<{}/{}> entered".format(
                    func_name,
                    ", ".join(["{}=%D".format(name) for name in argnames])
                ), *args)
            else:
                Logger.format("<{}> entered".format(func_name))

            if profile:
                repl_monitor_push(func_name, profile=True, log=False)

            # Call original function, and it should return None.
            # The violation would be checked by AppCommand object
            ret = old_func(self, *args)

            fmtstring = "<{}> exited".format(func_name)
            args = []
            if profile:
                tickdiff, expected = repl_monitor_pop()
                fmtstring += ", %D ms (Expected %D)"
                args += [tickdiff, expected]

            Logger.format(fmtstring, *args)

            return ret
        return new_func
    appcmd.set_func_callback(cb)
