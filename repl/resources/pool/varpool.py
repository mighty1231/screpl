from eudplib import *
from ...utils import f_raiseError

SIZE = 200
_varpool = None
class VarPool:
	def __init__(self, size):
		# EUDVArray: 72 byte for each variable
		self.size = size
		self.data = EUDVArray(size)([0 for _ in range(size)])
		self.cur_ptr = EUDVariable(self.data._value)
		self.alloc_history = EUDStack()(40)

	@EUDTypedMethod([None], [EUDVArray(0)])
	def alloc(self, sz):
		ret = EUDVariable()
		ret << self.cur_ptr

		self.alloc_history.push(self.cur_ptr)
		self.cur_ptr += sz * 72
		if EUDIf()(self.cur_ptr >= (self.data._value + 72*self.size)):
			f_raiseError("SC_REPL ERROR - VarPool.Alloc()")
		EUDEndIf()
		EUDReturn(ret)

	@EUDMethod
	def free(self, ptr):
		last_ptr = self.alloc_history.pop()

		if EUDIfNot()(ptr == last_ptr):
			f_raiseError("SC_REPL ERROR - VarPool.Free()")
		EUDEndIf()
		self.cur_ptr << last_ptr


def getVarPool():
	global _varpool
	if _varpool == None:
		_varpool = VarPool(SIZE)
	return _varpool
