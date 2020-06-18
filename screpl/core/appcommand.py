import inspect

from eudplib import *
from eudplib.core.eudfunc.eudtypedfuncn import EUDTypedFuncN
from eudplib.core.eudstruct.vararray import EUDVArrayData
from eudplib.core.eudfunc.eudfptr import createIndirectCaller

from screpl.encoder.encoder import ArgEncoderPtr, read_name, _read_until_delimiter
from screpl.utils.debug import f_epdsprintf
from screpl.utils.referencetable import search_table
from screpl.utils.string import f_strcmp_ptrepd

_MAXARGCNT = 8

_argn = EUDVariable()
_arg_encoders = EUDArray(_MAXARGCNT)
_arg_storage = EUDArray(_MAXARGCNT)


# Used as global variable during parsing iteratively
_offset = EUDVariable()
_encode_success = EUDVariable()

AppCommandPtr = EUDFuncPtr(0, 0)

_logbuf_epd = EUDVariable(0)

def run_app_command(manager, txtptr, logbuf_epd=None):
    _offset << txtptr
    if logbuf_epd:
        _logbuf_epd << logbuf_epd
    else:
        _logbuf_epd << 0

    # get current AppCommand table
    _run_app_command(manager.foreground_appstruct.cmdtable_epd)

@EUDFunc
def _run_app_command(cmdtable_epd):
    import screpl.apps.logger as logger
    funcname = Db(50)

    # read function name
    if EUDIf()(read_name(_offset, ord('('), \
            EPD(_offset.getValueAddr()), EPD(funcname)) == 1):
        func = AppCommandPtr()
        ret = EUDVariable()

        # search command
        if EUDIf()(search_table(funcname, cmdtable_epd, \
                f_strcmp_ptrepd, EPD(ret.getValueAddr())) == 1):

            # encode argument
            func.setFunc(AppCommandPtr.cast(ret))
            func()
        if EUDElse()():
            if EUDIf()(_logbuf_epd == 0):
                logger.Logger.format(
                    "run_app_command(): failed to search function %E",
                    EPD(funcname))
            if EUDElse()():
                f_epdsprintf(
                    _logbuf_epd,
                    "run_app_command(): failed to search function %E",
                    EPD(funcname))
            EUDEndIf()
        EUDEndIf()
    if EUDElse()():
        if EUDIf()(_logbuf_epd == 0):
            logger.Logger.format("run_app_command(): failed to read command")
        if EUDElse()():
            f_epdsprintf(_logbuf_epd,
                         "run_app_command(): failed to read command")
        EUDEndIf()
    EUDEndIf()

@EUDFunc
def encode_arguments():
    import screpl.apps.logger as logger

    i, delim = EUDCreateVariables(2)
    i << 0
    _encode_success << 1
    if EUDIf()(_argn == 0):
        _encode_success << _read_until_delimiter(ord(' '), ord(')'))
        if EUDIfNot()(_encode_success):
            if EUDIf()(_logbuf_epd == 0):
                logger.Logger.format("SyntaxError")
            if EUDElse()():
                f_epdsprintf(_logbuf_epd, "SyntaxError")
            EUDEndIf()
        EUDEndIf()
    if EUDElse()():
        delim << ord(',')
        if EUDInfLoop()():
            EUDBreakIf(i == _argn)
            if EUDIf()(i == _argn-1):
                delim << ord(')')
            EUDEndIf()
            _arg_encoder_ptr = ArgEncoderPtr.cast(_arg_encoders[i])
            if EUDIfNot()(_arg_encoder_ptr(_offset, delim, \
                    EPD(_offset.getValueAddr()), \
                    EPD(_arg_storage)+i) == 1):
                _encode_success << 0 # failed to encode argument

                if EUDIf()(_logbuf_epd == 0):
                    logger.Logger.format(
                        "SyntaxError: during encoding argument[%D] \x16%:strn;...",
                        i, (_offset, 5))
                if EUDElse()():
                    f_epdsprintf(
                        _logbuf_epd,
                        "SyntaxError: during encoding argument[%D] \x16%:strn;...",
                        i, (_offset, 5))
                EUDEndIf()
                EUDBreak()
            EUDEndIf()
            i += 1
        EUDEndInfLoop()
    EUDEndIf()

class AppCommandN:
    def __init__(self, arg_encoders, func, *, traced):
        # Get argument number of fdecl_func
        argspec = inspect.getfullargspec(func)

        if argspec.varargs:
            raise ValueError(
                "No variadic arguments (*args) allowed for AppCommandN")
        if argspec.varkw:
            raise ValueError(
                "No variadic keyword arguments (**kwargs) allowed for AppCommandN")

        self.arg_encoders = arg_encoders
        self.argn = len(arg_encoders)
        if self.argn > _MAXARGCNT:
            raise RuntimeError("Too many arguments!")

        self.func = func
        self.name = func.__qualname__
        self.cmd_ptr_val = EUDVArrayData(2)([0, 0])
        self.cmd_ptr = AppCommandPtr(self.cmd_ptr_val)

        # Step 2 initialize
        self.cls = None

        # Step 3 allocate
        self.funcn = None

        self.func_callback = None
        self.traced = traced
        self.status = 'not initialized'

    def __repr__(self):
        if self.status == 'not initialized':
            return '<AppCommand %s, st=NI>' % self.name
        elif self.status == 'initialized':
            return ('<AppCommand %s.%s, st=I>'
                    % (self.cls.__name__, self.name))
        elif self.status == 'allocated':
            return ('<AppCommand %s.%s, st=A>'
                    % (self.cls.__name__, self.name))
        else:
            raise RuntimeError

    def get_cmd_ptr(self):
        assert self.cls is not None
        return self.cmd_ptr

    def set_func_callback(self, func_callback):
        if self.status == "allocated":
            raise RuntimeError("AppCommand already has its body")
        assert self.func_callback is None
        self.func_callback = func_callback

    def initialize(self, cls):
        assert self.status == 'not initialized'
        self.cls = cls
        self.status = 'initialized'

    def allocate(self, manager):
        assert self.status == 'initialized'

        if self.func_callback:
            self.func = self.func_callback(self.func)

        def call_inner():
            instance = manager.get_foreground_app_instance()
            prev_cls = instance._cls
            instance._cls = self.cls

            _argn << self.argn
            for i, enc in enumerate(self.arg_encoders):
                _arg_encoders[i] = enc
            encode_arguments()

            if EUDIf()(_encode_success == 1):
                encoded_args = [_arg_storage[i] for i in range(self.argn)]
                ret = self.func(instance, *encoded_args)
            EUDEndIf()

            instance._cls = prev_cls
            return ret

        funcn = EUDTypedFuncN(
            0, call_inner, self.func, [], [],
            traced=self.traced)

        funcn._CreateFuncBody()
        f_idcstart, f_idcend = createIndirectCaller(funcn)
        assert funcn._retn == 0, "You should not return anything on AppCommand"

        self.funcn = funcn
        self.cmd_ptr_val._initvars = [f_idcstart, EPD(f_idcend + 4)]

        self.status = 'allocated'

''' Decorator to make AppMethodN '''
def AppCommand(arg_encoders, *, traced=False):
    def ret(method):
        return AppCommandN(arg_encoders, method, traced=traced)
    return ret
