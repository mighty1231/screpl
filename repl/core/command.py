from eudplib import *
from eudplib.core.eudfunc.eudfptr import callFuncBody

from ..utils import EPDConstString, f_strcmp_ptrepd
from .encoder import ArgEncoderPtr, _read_until_delimiter, ReadName
from .decoder import RetDecoderPtr, _output_writer
from .referencetable import ReferenceTable, SearchTable

import inspect
import functools

_MAXARGCNT = 8
_MAXRETCNT = 8

# variables for EUDCommand
_argn = EUDVariable()
_arg_encoders = EUDArray(_MAXARGCNT)
_arg_storage = EUDArray(_MAXARGCNT)

_retn = EUDVariable()
_ret_decoders = EUDArray(_MAXRETCNT)
_ret_storage = EUDArray(_MAXRETCNT)

# Used as global variable during parsing iteratively
_offset = EUDVariable()
_encode_success = EUDVariable()

# repl commands are stored
_repl_commands = ReferenceTable(key_f=EPDConstString)
def registerCommand(cmdname, command):
	_repl_commands.AddPair(cmdname, command)

@EUDFunc
def runCommand(txtptr, cmdtable_epd, ref_stdout_epd):
	funcname = Db(50)
	if EUDIf()(ReadName(txtptr, ord('('), \
			EPD(txtptr.getValueAddr()), EPD(funcname)) == 1):
		func = EUDCommandPtr()
		ret = EUDVariable()

		if EUDIf()(SearchTable(funcname, cmdtable_epd, \
				f_strcmp_ptrepd, EPD(ret.getValueAddr())) == 1):
			func << EUDCommandPtr.cast(ret)
			func(txtptr, ref_stdout_epd)
		if EUDElse()():
			_output_writer.seekepd(ref_stdout_epd)
			_output_writer.write_strepd(EPDConstString('\x06Failed to read function name'))
			_output_writer.write(0)
		EUDEndIf()
	if EUDElse()():
		_output_writer.seekepd(ref_stdout_epd)
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
				_output_writer.write_strepd(EPDConstString(\
						'\x06Syntax Error: during encoding argument ['))
				_output_writer.write_decimal(i)
				_output_writer.write_strepd(EPDConstString('] \x16'))
				_output_writer.write_strn(_offset, 5)
				_output_writer.write_strepd(EPDConstString('...'))
				_output_writer.write(0)
				EUDBreak()
			EUDEndIf()
			i += 1
		EUDEndInfLoop()
	EUDEndIf()

@EUDFunc
def decodeReturns():
	i = EUDVariable()
	i << 0
	if EUDInfLoop()():
		EUDBreakIf(i == _retn)
		if EUDIf()(i >= 1):
			_output_writer.write_strepd(EPDConstString(', '))
		EUDEndIf()

		_ret_decoder_ptr = RetDecoderPtr.cast(_ret_decoders[i])
		_ret_decoder_ptr(_ret_storage[i])
		i += 1
	EUDEndInfLoop()
	_output_writer.write(0)

@cachedfunc
def createIndirectCaller(f):
	""" Create function caller using common argument/return storage """

	# Cache function in _caller_dict. If uncached,
	PushTriggerScope()
	caller_start = NextTrigger()

	# set argument encoders
	_argn << f._argn
	for i, enc in enumerate(f.arg_encoders):
		_arg_encoders[i] = enc
	encodeArguments()
	if EUDIf()(_encode_success == 1):
		""" Copy values from common argument storage to f._args """
		for i, farg in enumerate(f._fargs):
			farg << _arg_storage[i]
		callFuncBody(f._fstart, f._fend)

		# set retval decoders
		if f._retn:
			_retn << f._retn
			for i in range(f._retn):
				_ret_decoders[i] = f.ret_decoders[i]
				_ret_storage[i] = f._frets[i]

			# print result to output buffer
			decodeReturns()
		else:
			_output_writer.write_strepd(EPDConstString('Success!'))
			_output_writer.write(0)
	EUDEndIf()
	caller_end = RawTrigger()
	PopTriggerScope()

	return caller_start, caller_end

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
		return EUDCommandPtr(ret)

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
		doc = inspect.getdoc(func)
		if doc != None:
			assert '\n' not in doc, "document should be one-line"
		else:
			doc = ', '.join(inspect.getargspec(func)[0])
		self._doc_epd = EPDConstString(doc)

class EUDCommandPtr(EUDStruct):
	_fields_ = [
		'_fstart',
		'_fendnext_epd',
		'_doc_epd',
	]

	def __init__(self, _from = None):
		basetype = type(self)
		fields = basetype._fields_

		# Fill fielddict
		fielddict = {}
		for index, nametype in enumerate(fields):
			if isinstance(nametype, str):
				fielddict[nametype] = (index, None)
			else:
				fielddict[nametype[0]] = (index, nametype[1])
		self._fielddict = fielddict

		if _from is not None:
			if isinstance(_from, EUDCommandN):
				self.checkValidFunction(_from)
				f_idcstart, f_idcend = createIndirectCaller(_from)
				ExprProxy.__init__(self, EUDVArray(3)(\
						[f_idcstart, EPD(f_idcend + 4), _from._doc_epd]))
				self._initialized = True
			else: # EUDVariable things
				ExprProxy.__init__(self, EUDVArray(3).cast(_from))
				self._initialized = True
		else:
			ExprProxy.__init__(self, EUDVArray(3)([0] * len(fields)))
			self.isPooled = False
			self._initialized = True

	@classmethod
	def cast(cls, _from):
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
			self._doc_epd = f._doc_epd

		except AttributeError:
			self.checkValidFunction(f)

			# Build actions
			f_idcstart, f_idcend = createIndirectCaller(f)
			self._fstart = f_idcstart
			self._fendnext_epd = EPD(f_idcend + 4)
			self._doc_epd = f._doc_epd

	def __lshift__(self, rhs):
		self.setFunc(rhs)

	def __call__(self, offset, ref_stdout_epd):
		"""Call target function with given offset ptr for string
		This call can change offset
		Returns 1 if it parsed offset successfully and call function
		Otherwise 0
		"""
		_offset << offset
		_output_writer.seekepd(ref_stdout_epd)

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
