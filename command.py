# This library should be imported during *TriggerExec
# Otherwise, error happens - IndexError: list index out of range 

from eudplib import *
from utils import *
from eudplib.core.eudfunc.eudfptr import callFuncBody
import inspect
import functools

__all__ = ['EUDCommand', 'EUDCommandPtr', 'EUDCommandStruct']

_MAXARGCNT = 8
_MAXRETCNT = 8
_output_writer = EUDByteRW()
_error_writer = EUDByteRW()

# variables for outer function
from encoder import ArgEncoderPtr, _reader, _read_until_delimiter
_argn = EUDVariable()
_arg_encoders = EUDArray(_MAXARGCNT)

from decoder import RetDecoderPtr
_retn = EUDVariable()
_ret_decoders = EUDArray(_MAXRETCNT)

# Used as global variable during parsing iteratively
_offset = EUDVariable()
_encoded = EUDVariable()
_refoffset_epd = EPD(_offset.getValueAddr())
_refencoded = EPD(_encoded.getValueAddr())

_encode_success = EUDVariable()

# store arguments/returned values from inner function
_arg_storage = EUDArray(_MAXARGCNT)
_ret_storage = EUDArray(_MAXRETCNT)

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
			if EUDIf()(_arg_encoder_ptr(_offset, delim, _refoffset_epd, _refencoded) == 1):
				_arg_storage[i] = _encoded
			if EUDElse()():
				_encode_success << 0 # failed to encode argument
				_output_writer.write_str(makeText(\
						'\x06Syntax Error: during encoding argument ['))
				_output_writer.write_decimal(i)
				_output_writer.write_str(makeText('] \x16'))
				_output_writer.write_strn(_offset, 5)
				_output_writer.write_str(makeText('...'))
				_output_writer.write(0)
				EUDBreak()
			EUDEndIf()
			i += 1
		EUDEndInfLoop()
	EUDEndIf()

def fillArguments(f):
	""" Copy values from common argument storage to f._args """
	for i, farg in enumerate(f._fargs):
		farg << _arg_storage[i]

@EUDFunc
def decodeReturns():
	i = EUDVariable()
	i << 0
	if EUDInfLoop()():
		EUDBreakIf(i == _retn)
		if EUDIf()(i >= 1):
			_output_writer.write_str(makeText(', '))
		EUDEndIf()

		_ret_decoder_ptr = RetDecoderPtr.cast(_ret_decoders[i])
		_ret_decoder_ptr(_ret_storage[i])
		i += 1
	EUDEndInfLoop()
	_output_writer.write(0)

def createIndirectCaller(f, _caller_dict={}):
	""" Create function caller using common argument/return storage """

	# Cache function in _caller_dict. If uncached,
	if f not in _caller_dict:
		PushTriggerScope()
		caller_start = NextTrigger()

		# set argument encoders
		_argn << f._argn
		for i, enc in enumerate(f.arg_encoders):
			_arg_encoders[i] = ArgEncoderPtr(enc)
		encodeArguments()
		if EUDIf()(_encode_success == 1):
			fillArguments(f)
			callFuncBody(f._fstart, f._fend)

			# set retval decoders
			if f._retn:
				_retn << f._retn
				for i in range(f._retn):
					_ret_decoders[i] = RetDecoderPtr(f.ret_decoders[i])
					_ret_storage[i] = f._frets[i]

				# print result to output buffer
				decodeReturns()
			else:
				_output_writer.write_str(makeText('Successful'))
				_output_writer.write(0)
		EUDEndIf()
		caller_end = RawTrigger()
		PopTriggerScope()

		_caller_dict[f] = (caller_start, caller_end)

	return _caller_dict[f]

def EUDCommand(arg_encoders, ret_decoders = [], *, traced=False):
    def _EUDCommand(fdecl_func):
        argspec = inspect.getargspec(fdecl_func)
        argn = len(argspec[0])
        ep_assert(
            argspec[1] is None,
            'No variadic arguments (*args) allowed for EUDCommand.'
        )
        ep_assert(
            argspec[2] is None,
            'No variadic keyword arguments (*kwargs) allowed for EUDCommand.'
        )

        ret = EUDCommandN(
            argn, fdecl_func,
            arg_encoders, ret_decoders,
            traced=traced
        )
        functools.update_wrapper(ret, fdecl_func)
        return ret

    return _EUDCommand

class EUDCommandN(EUDFuncN):

	"""
	EUDFuncN specialization for EUDCommandN. This will pre-convert
	arguments to types prior to function call.
	"""
	def __init__(self, argn, func, arg_encoders, ret_decoders,
				*, traced):
		super().__init__(argn, func, func, traced=traced)
		assert argn <= _MAXARGCNT, "argument number should be <= %d" % _MAXARGCNT
		assert argn == len(arg_encoders), \
			"Mismatch of length between arg_encoders and function arguments"

		self.arg_encoders = arg_encoders
		self.ret_decoders = ret_decoders

class EUDCommandPtr(EUDStruct):
	_fields_ = [
		'_fstart',
		'_fendnext_epd',
	]

	def constructor(*args, **kwargs):
		raise NotImplemented

	def constructor_static(self, f_init = None):
		if f_init:
			self.checkValidFunction(f_init)
			f_idcstart, f_idcend = createIndirectCaller(f_init)
			self._fstart = f_idcstart
			self._fendnext_epd = EPD(f_idcend + 4)

	@classmethod
	def cast(cls, _from):
		# Special casting rule: EUDCommandN → EUDCommandPtr
		# I'm not sure it is right
		if isinstance(_from, EUDCommandN):
			return cls(_from)
		else:
			return cls(_from=_from)

	def checkValidFunction(self, f):
		ep_assert(isinstance(f, EUDCommandN), "%s is not an EUDCommandN" % f)
		if not f._fstart:
			f._CreateFuncBody()

		f_argn = f._argn
		f_retn = f._retn
		ep_assert(f_argn <= _MAXARGCNT, "argument count(%d) should be <= %d" %
					 (f_argn, _MAXARGCNT))
		ep_assert(f_retn <= _MAXRETCNT, "retval count(%d) should be <= %d" %
					 (f_retn, _MAXRETCNT))


	def setFunc(self, f):
		""" Set function pointer's target to function
		:param f: Target function
		"""
		try:
			self._fstart, self._fendnext_epd = f._fstart, f._fendnext_epd

		except AttributeError:
			self.checkValidFunction(f)

			# Build actions
			f_idcstart, f_idcend = createIndirectCaller(f)
			self._fstart = f_idcstart
			self._fendnext_epd = EPD(f_idcend + 4)

	def __lshift__(self, rhs):
		self.setFunc(rhs)

	def __call__(self, offset, ref_stdout_epd, ref_stderr_epd):
		"""Call target function with given offset ptr for string
		This call can change offset
		Returns 1 if it parsed offset successfully and call function
		Otherwise 0
		"""
		DoActions(SetMemoryEPD(_refoffset_epd, SetTo, offset))
		_output_writer.seekepd(ref_stdout_epd)
		_error_writer.seekepd(ref_stderr_epd)

		# Call function
		t, a = Forward(), Forward()
		SetVariables(
			[EPD(t + 4), EPD(a + 16)],
			[self._fstart, self._fendnext_epd]
		)

		fcallend = Forward()
		t << RawTrigger(
			actions=[
				a << SetNextPtr(0, fcallend),
			]
		)
		fcallend << NextTrigger()

		# return
		tmpRet = EUDVariable()
		SetVariables([tmpRet], [_encode_success])
		return tmpRet

class EUDCommandStruct(EUDStruct):
	_fields_ = [
		'cmdname', 
		('cmdptr', EUDCommandPtr),
	]

	def constructor(*args, **kwargs):
		raise NotImplemented

	def constructor_static(self, cmdname, cmdn):
		if isinstance(cmdname, Db):
			self.cmdname = cmdname
		elif isinstance(cmdname, str):
			self.cmdname = makeText(cmdname)
		else:
			raise RuntimeError()
		self.cmdptr = EUDCommandPtr(cmdn)
