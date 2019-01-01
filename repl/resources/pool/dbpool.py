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
		self.alloc_cnt = EUDVariable(0)
		self.alloc_history = EUDArray(200)

	@EUDMethod
	def alloc_epd(self, sz):
		ret = EUDVariable()
		ret << self.cur_epd

		# push on history stack
		self.alloc_history[self.alloc_cnt] = self.cur_epd
		self.alloc_cnt += 1
		self.cur_epd += sz
		if EUDIf()(self.cur_epd >= (EPD(self.data) + self.size)):
			f_raiseError("SC_REPL ERROR - DbPool.Alloc()")
		EUDEndIf()
		EUDReturn(ret)

	@EUDMethod
	def free_epd(self, epd):
		# pop on history stack
		self.alloc_cnt -= 1
		last_epd = self.alloc_history[self.alloc_cnt]
		if EUDIfNot()(epd == last_epd):
			f_raiseError("SC_REPL ERROR - DbPool.Free()")
		EUDEndIf()
		self.cur_epd << last_epd

	@EUDMethod
	def print_status(self):
		f_simpleprint(*(['dbpool', self.alloc_cnt]+[self.alloc_history[i] for i in range(10)]))


def getDbPool():
	global _dbpool
	if _dbpool == None:
		_dbpool = DbPool(SIZE)
	return _dbpool
