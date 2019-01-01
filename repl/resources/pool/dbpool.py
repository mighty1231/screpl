from eudplib import *
from ...utils import f_raiseError

SIZE = 100000
_dbpool = None
class DbPool:
	def __init__(self, size):
		# EUDVArray: 72 byte for each variable
		self.size = size
		self.data = EUDArray([0 for _ in range(size)])
		self.cur_epd = EUDVariable(EPD(self.data))
		self.alloc_history = EUDStack()(200)

	@EUDMethod
	def alloc_epd(self, sz):
		ret = EUDVariable()
		ret << self.cur_epd

		self.alloc_history.push(self.cur_epd)
		self.cur_epd += sz
		if EUDIf()(self.cur_epd >= (EPD(self.data) + self.size)):
			f_raiseError("SC_REPL ERROR - DbPool.Alloc()")
		EUDEndIf()
		EUDReturn(ret)

	@EUDMethod
	def free_epd(self, epd):
		last_epd = self.alloc_history.pop()

		if EUDIfNot()(epd == last_epd):
			f_raiseError("SC_REPL ERROR - DbPool.Free()")
		EUDEndIf()
		self.cur_epd << last_epd


def getDbPool():
	global _dbpool
	if _dbpool == None:
		_dbpool = DbPool(SIZE)
	return _dbpool
