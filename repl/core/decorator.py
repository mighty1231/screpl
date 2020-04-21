from eudplib import *

from .logger import Logger

def IOCheck(func):
    if isinstance(func, EUDFuncN):
        return decoEUDFuncN(func)
    elif isinstance(func, AppMethod):
        return decoAppMethod(func)
    elif isinstance(func, AppCommand):
        return decoAppCommand(func)
    raise RuntimeError("IOCheck can be done with EUDFuncN, AppCommand, AppMethod")

def decoEUDFuncN(funcn):
    if funcn._fstart:
        raise RuntimeError("EUDFuncN already has its body")

    funcn_name = funcn._bodyfunc
    old_caller = funcn._callerfunc
    def new_caller(*args):
        _inputs = EUDCreateVariables(funcn._argn)
        for i, v in zip(_inputs, args):
            i << v

        final_rets = old_caller(*args)

        if final_rets is not None:
            funcn._AddReturn(Assignable2List(final_rets), False)
        funcn._fend << NextTrigger() # To catch EUDReturn

        _outputs = EUDCreateVariables(funcn._retn)
        for i, v in zip(_outputs, funcn._frets):
            i << v

        # Log format: myfunction(arg1, arg2) -> (ret1, ret2)
        fmtstring = "{}({}) -> ({})".format(
            funcn_name,
            ", ".join(["%D"] * funcn._argn),
            ", ".join(["%D"] * funcn._retn)
        )
        Logger.fmt(fmtstring, *(_inputs + _outputs))

        funcn._fend = Forward()
        return None
    funcn._callerfunc = new_caller
    return funcn

def _decoAppMethod(funcn):
    if funcn._fstart:
        raise RuntimeError("EUDFuncN already has its body")

    old_caller = funcn._callerfunc
    def new_caller(*args):
        _inputs = EUDCreateVariables(funcn._argn)
        for i, v in zip(_inputs, args):
            i << v

        final_rets = old_caller(*args)

        if final_rets is not None:
            funcn._AddReturn(Assignable2List(final_rets), False)
        funcn._fend << NextTrigger()

        _outputs = EUDCreateVariables(funcn._retn)
        for i, v in zip(_outputs, funcn._frets):
            i << v

        # Log format: my_app.my_method(arg1, arg2) -> (ret1, ret2)
        fmtstring = "{}({}) -> ({})".format(
            funcn._bodyfunc.__qualname__,
            ", ".join(["%D"] * funcn._argn),
            ", ".join(["%D"] * funcn._retn)
        )
        Logger.fmt(fmtstring, *(_inputs + _outputs))

        funcn._fend = Forward()
        return None
    funcn._callerfunc = new_caller
    return funcn

def decoAppCommand(cmd):
    if cmd.status == "allocated":
        raise RuntimeError("AppCommand already has its body")

    old_func = cmd.func
    def new_func(self, *args):
        assert isinstance(self, ApplicationInstance)
        _inputs = EUDCreateVariables(cmd.argn)
        for i, v in zip(_inputs, args):
            i << v

        # Log format: my_app.my_cmd(arg1, arg2)
        fmtstring = "{}.{}({})".format(
            cmd.cls,
            cmd.func.__name__,
            ", ".join(["%D"] * funcn._argn)
        )
        Logger.fmt(fmtstring, *_inputs)

        return old_func(self, *args)

    cmd.func = new_func
    return cmd
