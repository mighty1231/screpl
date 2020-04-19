from eudplib import *

from eudplib.core.eudfunc.eudtypedfuncn import EUDTypedFuncN
from .appmanager import getAppManager
from .encoder import ArgEncoderPtr, ReadName, _read_until_delimiter
from .eudbyterw import EUDByteRW
from .referencetable import SearchTable
from ..utils import EPDConstString, f_strcmp_ptrepd

import inspect

_MAXARGCNT = 8

_argn = EUDVariable()
_arg_encoders = EUDArray(_MAXARGCNT)
_arg_storage = EUDArray(_MAXARGCNT)


# Used as global variable during parsing iteratively
_offset = EUDVariable()
_encode_success = EUDVariable()
_output_writer = EUDByteRW()
_ref_stdout_epd = EUDVariable()

AppCommandPtr = EUDFuncPtr(0, 0)

def runAppCommand(txtptr, ref_stdout_epd):
    _offset << txtptr
    _ref_stdout_epd << ref_stdout_epd
    _runAppCommand()

@EUDFunc
def _runAppCommand():
    cmdtable_epd = getAppManager().cur_cmdtable_epd
    funcname = Db(50)
    _output_writer.seekepd(_ref_stdout_epd)

    # read function name
    if EUDIf()(ReadName(_offset, ord('('), \
            EPD(_offset.getValueAddr()), EPD(funcname)) == 1):
        func = AppCommandPtr()
        ret = EUDVariable()

        # search command
        if EUDIf()(SearchTable(funcname, cmdtable_epd, \
                f_strcmp_ptrepd, EPD(ret.getValueAddr())) == 1):

            # encode argument
            func.setFunc(AppCommandPtr.cast(ret))
            func()
        if EUDElseIfNot()(_ref_stdout_epd == 0):
            _output_writer.write_strepd(EPDConstString('\x06Failed to read function name'))
            _output_writer.write(0)
        EUDEndIf()
    if EUDElseIfNot()(_ref_stdout_epd == 0):
        _output_writer.write_strepd(EPDConstString('\x06Failed to read command'))
        _output_writer.write(0)
    EUDEndIf()

@EUDFunc
def encodeArguments():
    i, delim = EUDCreateVariables(2)
    i << 0
    _encode_success << 1
    if EUDIf()(_argn == 0):
        _encode_success << _read_until_delimiter(ord(' '), ord(')'))
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
                if EUDIfNot()(_ref_stdout_epd == 0):
                    _output_writer.write_strepd(EPDConstString(\
                            '\x06Syntax Error: during encoding argument ['))
                    _output_writer.write_decimal(i)
                    _output_writer.write_strepd(EPDConstString('] \x16'))
                    _output_writer.write_strn(_offset, 5)
                    _output_writer.write_strepd(EPDConstString('...'))
                    _output_writer.write(0)
                EUDEndIf()
                EUDBreak()
            EUDEndIf()
            i += 1
        EUDEndInfLoop()
    EUDEndIf()

class _AppCommand:
    def __init__(self, arg_encoders, func, *, traced):
        # Get argument number of fdecl_func
        argspec = inspect.getargspec(func)
        ep_assert(
            argspec[1] is None,
            'No variadic arguments (*args) allowed for AppCommand.'
        )
        ep_assert(
            argspec[2] is None,
            'No variadic keyword arguments (*kwargs) allowed for AppCommand.'
        )

        self.arg_encoders = arg_encoders
        self.argn = len(arg_encoders)

        self.func = func
        self.cmdptr = AppCommandPtr()

        # Step 2 initialize
        self.cls = None

        # Step 3 allocate
        self.funcn = None

        self.traced = traced
        self.status = 'not initialized'

    def getCmdPtr(self):
        assert self.cls is not None
        return self.cmdptr

    def initialize(self, cls):
        assert self.status == 'not initialized'
        self.cls = cls
        self.status = 'initialized'

    def allocate(self):

        assert self.status == 'initialized'

        def call_inner():
            instance = getAppManager().getCurrentAppInstance()
            prev_cls = instance._cls
            instance._cls = self.cls

            _argn << self.argn
            for i, enc in enumerate(self.arg_encoders):
                _arg_encoders[i] = enc
            encodeArguments()

            if EUDIf()(_encode_success == 1):
                encoded_args = [_arg_storage[i] for i in range(self.argn)]
                ret = self.func(instance, *encoded_args)
                assert ret is None, "You should not return anything on AppCommand"
            EUDEndIf()

            instance._cls = prev_cls

        self.funcn = EUDTypedFuncN(
            0, call_inner, self.func, [], [],
            traced=self.traced)
        self.cmdptr << self.funcn
        assert self.funcn._retn == 0, "You should not return anything on AppCommand"

        self.status = 'allocated'

''' Decorator to make _AppMethod '''
def AppCommand(arg_encoders, *, traced=False):
    def ret(method):
        return _AppCommand(arg_encoders, method, traced=traced)
    return ret
