from eudplib import *
from .pool import DbPool, VarPool
from ..utils import EUDByteRW, makeEPDText

_textPool = DbPool(300000)
_varPool = VarPool(600)
LINESIZE = 216

class ScrollView(EUDStruct):
	_fields_ = [
		'_allocated', # 1 if it uses _textPool, otherwise 0

		'lines_per_page', # default: 8
		'max_lcnt', # maximum lines, some may be reserved
		'disp_lcnt', # display line 0 ~ disp_lcnt-1, others are reserved

		'epd_lines', # EPD value for EUDArray of EPD(Db)

		'offset',
	]
	def __init__(self, *args, _from = None, lines_per_page = 8):
		if _from is not None:
			super().__init__(_from = _from)
		else:
			super().__init__(_from = _varPool.alloc(\
				len(ScrollView._fields_)))
			if len(args) == 1:
				if isinstance(args[0], int) or \
						isinstance(args[0], EUDVariable):
					# interpret it as count of lines
					lcnt = args[0]
					self._allocated = 1
					self.lines_per_page = lines_per_page

					self.max_lcnt = lcnt
					self.disp_lcnt = lcnt
					self.epd_lines = _textPool.alloc_epd(4 * lcnt)

					# fill epd_lines
					buf_epd = _textPool.alloc_epd(lcnt * LINESIZE)
					dest_epd = self.epd_lines
					i = EUDVariable()
					i << 0
					if EUDWhile()(i < lcnt):
						f_dwwrite_epd(dest_epd, buf_epd)
						DoActions([
							i.AddNumber(1),
							dest_epd.AddNumber(1),
							buf_epd.AddNumber(LINESIZE // 4)
						])
					EUDEndWhile()

					self.offset = 0
				elif isinstance(args[0], str):
					# static construction from string
					text = args[0]
					self._allocated = 0
					self.lines_per_page = lines_per_page

					arr = [makeEPDText(line) for line in text.split('\n')]
					self.max_lcnt = len(arr)
					self.disp_lcnt = len(arr)
					self.epd_lines = EPD(EUDArray(arr))
					self.offset = 0
				else:
					raise RuntimeError
			else:
				# construction from line cnt, EUDArray with EPD texts
				lcnt, epdarr = args
				self._allocated = 0
				self.lines_per_page = lines_per_page

				self.max_lcnt = lcnt
				self.disp_lcnt = lcnt
				self.epd_lines = epdarr
				self.offset = 0

	@EUDMethod
	def Destruct(self):
		if EUDIf()(self._allocated == 1):
			_textPool.free_epd(f_dwread_epd(self.epd_lines))
			_textPool.free_epd(self.epd_lines)
		EUDEndIf()
		_varPool.free(self)

	def GetEPDLine(self, i):
		return f_dwread_epd(self.epd_lines + i)

	def SetDispLineCnt(self, cnt):
		self.disp_lcnt = cnt

	@EUDMethod
	def Display(self):
		# print offset ~ offset + lines_per_page - 1
		# similar to DBString in eudplib
		#   but no conversion from cp949 to utf8
		sp = EUDVariable(0)
		strId = EncodeString("_" * 2048)
		if EUDExecuteOnce()():
			sp << GetMapStringAddr(strId)
		EUDEndExecuteOnce()

		writer = EUDByteRW()
		writer.seekoffset(sp)

		cur, pageend, until = EUDCreateVariables(3)
		cur << self.offset
		pageend << self.offset + self.lines_per_page
		if EUDIf()(pageend >= self.disp_lcnt):
			until << self.disp_lcnt
		if EUDElse()():
			until << pageend
		EUDEndIf()

		# Fill with contents
		if EUDInfLoop()():
			EUDBreakIf(cur >= until)
			writer.write_strepd(f_dwread_epd(self.epd_lines + cur))
			writer.write(ord('\n'))

			DoActions(cur.AddNumber(1))
		EUDEndInfLoop()

		# Fill with empty lines
		if EUDInfLoop()():
			EUDBreakIf(cur >= pageend)
			writer.write(ord('\n'))
			DoActions(cur.AddNumber(1))
		EUDEndInfLoop()
		writer.write(0)

		# Display to current player
		DoActions(DisplayText(strId))

	@EUDMethod
	def SetOffset(self, offset):
		if EUDIf()(self.disp_lcnt <= self.lines_per_page):
			self.offset = 0
		if EUDElseIf()(offset > 0x80000000):
			self.offset = 0
		if EUDElse()():
			if EUDIfNot()(offset >= self.disp_lcnt - self.lines_per_page):
				self.offset = offset
			if EUDElse()():
				self.offset = self.disp_lcnt - self.lines_per_page
			EUDEndIf()
		EUDEndIf()

	def SetNextPage(self):
		self.SetOffset(self.offset + self.lines_per_page)

	def SetPrevPage(self):
		self.SetOffset(self.offset - self.lines_per_page)
