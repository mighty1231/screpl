from eudplib import *
from .core.pool import DbPool, VarPool
from ..utils import f_raiseError, makeEPDText

_textPool = DbPool(300000)
_varPool = VarPool(600)
LINESIZE = 216

class ScrollableText(EUDStruct):
	_fields_ = [
		'_allocated', # 1 if it uses _textPool, otherwise 0

		'lines_per_page', # default: 8
		'max_ln', # maximum lines, some may be reserved
		'disp_ln', # display line 0 ~ disp_ln-1, others are reserved

		('epd_lines', EUDArray), # Array of EPD(Db)

		'offset',
	]
	def __init__(self, lines, lines_per_page = 8):
		super().__init__(_from = _varPool.alloc(6))
		if isinstance(lines, int):
			# interpret it as count of lines
			self._allocated = 1
			self.lines_per_page = lines_per_page

			self.max_ln = lines
			self.disp_ln = lines
			self.epd_lines = _textPool.alloc_epd(4 * lines)

			# fill epd_lines
			self.epd_lines[0] = _textPool.alloc_epd(lines * LINESIZE)
			i = EUDVariable(1)
			line_epd = self.epd_lines[0] + (LINESIZE // 4)
			if EUDWhile()(i < lines):
				self.epd_lines[i] = line_epd
				DoActions([
					i.AddNumber(1),
					line_epd.AddNumber(LINESIZE // 4)
				])
			EUDEndWhile()

			self.offset = 0
		elif isinstance(lines, str):
			# static construction from string
			self._allocated = 0
			self.lines_per_page = lines_per_page

			arr = [makeEPDText(line) for line in lines.split('\n')]
			self.max_ln = len(arr) 
			self.disp_ln = len(arr)
			self.epd_lines = EUDArray(arr)
			self.offset = 0
		else:
			raise RuntimeError

	@EUDMethod
	def Destruct(self):
		if EUDIf()(self._allocated == 1):
			_textPool.free_epd(self.epd_lines[0])
			_textPool.free_epd(self.epd_lines)
		EUDEndIf()
		_varPool.free(self)

	def GetEPDLine(self, i):
		return self.epd_lines[i]

	def SetDispLineCnt(self, cnt):
		self.disp_ln = cnt

	def Display(self):
		# print offset ~ lines_per_page
		pass

	def SetOffset(self, offset):
		if EUDIf()(offset <= 0x7FFFFFFF):
			if EUDIfNot()(offset >= self.disp_ln - self.lines_per_page):
				self.offset = offset
			if EUDElse()():
				self.offset = self.disp_ln - self.lines_per_page
			EUDEndIf()
		if EUDElse()():
			self.offset = 0
		EUDEndIf()

	def SetNextPage(self):
		self.SetOffset(self.offset + self.lines_per_page)

	def SetPrevPage(self):
		self.SetOffset(self.offset - self.lines_per_page)
