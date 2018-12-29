from eudplib import *

def makeText(msg):
	if not hasattr(makeText, 'textdict'):
		makeText.textdict = {}
	textdict = makeText.textdict
	try:
		return textdict[msg]
	except KeyError:
		textdict[msg] = Db(u2b(msg) + b'\0')
		return textdict[msg]

def makeTextEPDArray(txt):
	lines = []
	if type(txt) == str:
		lines = txt.split('\n')
	elif type(txt) == list:
		for line in txt:
			lines += line.split('\n')
	ln = len(lines)
	return EUDArray([EPD(makeText(line)) for line in lines]), ln

@EUDFunc
def f_dbepd_print(epd):
	a = DBString(1024)
	writer = EUDByteRW()
	writer.seekoffset(a.GetStringMemoryAddr())
	writer.write_strepd(epd)
	writer.write(0)
	a.Display()

@EUDFunc
def f_print_memorytable(off):
	f_simpleprint('Memory table offset = ', hptr(off))
	a = DBString(100)
	writer = EUDByteRW()
	writer.seekoffset(a.GetStringMemoryAddr())
	writer.write_strepd(EPD(makeText(' - ')))
	writer.write_memoryTable(off, 8)
	writer.write_strn(off, 8)
	writer.write(0)
	a.Display()

@EUDFunc
def f_epd2ptr(epd):
	EUDReturn(0x58A364 + epd * 4)

@EUDFunc
def f_print_memorytable_epd(epd):
	off = f_epd2ptr(epd)
	f_simpleprint('Memory table offset epd = ', hptr(off))
	a = DBString(100)
	writer = EUDByteRW()
	writer.seekoffset(a.GetStringMemoryAddr())
	writer.write_strepd(EPD(makeText(' - ')))
	writer.write_memoryTable(off, 8)
	writer.write_strn(off, 8)
	writer.write(0)
	a.Display()

@EUDFunc
def f_strcpy2(dest, src):
	''' s1, s2: ptr '''
	writer = EUDByteRW()
	writer.seekoffset(dest)
	writer.write_str(src)

@EUDFunc
def f_strcmp2(s1, s2):
	''' s1, s2: ptr '''
	cr1 = EUDByteRW()
	cr2 = EUDByteRW()

	cr1.seekoffset(s1)
	cr2.seekoffset(s2)

	if EUDInfLoop()():
		ch1 = cr1.read()
		ch2 = cr2.read()
		if EUDIf()(ch1 == ch2):
			if EUDIf()(ch1 == 0):
				EUDReturn(0)
			EUDEndIf()
			EUDContinue()
		if EUDElse()():
			EUDReturn(ch1 - ch2)
		EUDEndIf()
	EUDEndInfLoop()

@EUDFunc
def f_strcmp_epd(s1, s2):
	''' s1, s2: epd '''
	cr1 = EUDByteRW()
	cr2 = EUDByteRW()

	cr1.seekepd(s1)
	cr2.seekepd(s2)

	if EUDInfLoop()():
		ch1 = cr1.read()
		ch2 = cr2.read()
		if EUDIf()(ch1 == ch2):
			if EUDIf()(ch1 == 0):
				EUDReturn(0)
			EUDEndIf()
			EUDContinue()
		if EUDElse()():
			EUDReturn(ch1 - ch2)
		EUDEndIf()
	EUDEndInfLoop()

@EUDFunc
def f_strcmp_ptrepd(s1, s2):
	''' s1: ptr, s2: epd '''
	cr1 = EUDByteRW()
	cr2 = EUDByteRW()

	cr1.seekoffset(s1)
	cr2.seekepd(s2)

	if EUDInfLoop()():
		ch1 = cr1.read()
		ch2 = cr2.read()
		if EUDIf()(ch1 == ch2):
			if EUDIf()(ch1 == 0):
				EUDReturn(0)
			EUDEndIf()
			EUDContinue()
		if EUDElse()():
			EUDReturn(ch1 - ch2)
		EUDEndIf()
	EUDEndInfLoop()

@EUDFunc
def f_strlen(s):
	reader = EUDByteRW()
	cnt = EUDVariable()

	reader.seekoffset(s)
	cnt << 0
	if EUDInfLoop()():
		ch = reader.read()
		EUDBreakIf(ch == 0)
		DoActions(cnt.AddNumber(1))
	EUDEndInfLoop()
	EUDReturn(cnt)

@EUDFunc
def f_memcmp(p1, p2, cnt):
	''' p1, p2: ptr '''
	cr1 = EUDByteRW()
	cr2 = EUDByteRW()

	cr1.seekoffset(p1)
	cr2.seekoffset(p2)

	if EUDInfLoop()():
		EUDBreakIf(cnt == 0)
		ch1 = cr1.read()
		ch2 = cr2.read()
		if EUDIf()(ch1 == ch2):
			cnt -= 1
			EUDContinue()
		EUDEndIf()
		EUDReturn(ch1 - ch2)
	EUDEndInfLoop()
	EUDReturn(0)

class EUDByteRW:
	def __init__(self):
		self.epd, self.off = EUDCreateVariables(2)

	@EUDMethod
	def getoffset(self):
		EUDReturn(0x58A364 + 4 * self.epd + self.off)

	@EUDMethod
	def seekepd(self, epd):
		self.epd << epd
		self.off << 0

	@EUDMethod
	def seekoffset(self, ptr):
		epd, off = f_div(ptr, 4)
		epd += -0x58A364 // 4

		self.epd << epd
		self.off << off

	@EUDMethod
	def read(self):
		ret = EUDVariable()
		ret << 0

		EUDSwitch(self.off)
		if EUDSwitchCase()(0):
			for i in range(8):
				Trigger(
					conditions = MemoryXEPD(self.epd, Exactly, 2**i, 2**i),
					actions = ret.AddNumber(2**i)
				)
			self.off += 1
			EUDBreak()
		if EUDSwitchCase()(1):
			for i in range(8):
				Trigger(
					conditions = MemoryXEPD(self.epd, Exactly, 2**(i+8), 2**(i+8)),
					actions = ret.AddNumber(2**i)
				)
			self.off += 1
			EUDBreak()
		if EUDSwitchCase()(2):
			for i in range(8):
				Trigger(
					conditions = MemoryXEPD(self.epd, Exactly, 2**(i+16), 2**(i+16)),
					actions = ret.AddNumber(2**i)
				)
			self.off += 1
			EUDBreak()
		if EUDSwitchCase()(3):
			for i in range(8):
				Trigger(
					conditions = MemoryXEPD(self.epd, Exactly, 2**(i+24), 2**(i+24)),
					actions = ret.AddNumber(2**i)
				)
			DoActions([self.epd.AddNumber(1), self.off.SetNumber(0)])
			EUDBreak()
		EUDEndSwitch()
		EUDReturn(ret)

	@EUDMethod
	def write(self, val):
		_acts = [Forward() for _ in range(4)]
		_offvals = [0xFF, 0xFF00, 0xFF0000, 0xFF000000]
		DoActions([SetMemory(_act+20, SetTo, 0) for _act in _acts])
		for i in range(8):
			RawTrigger(
				conditions = [
					MemoryX(val.getValueAddr(), Exactly, 2**i, 2**i)
				],
				actions = [
					SetMemoryX(_acts[off]+20, Add, 2**(i+off*8), _offvals[off])
					for off in range(4)
				]
			)
		EUDSwitch(self.off)
		if EUDSwitchCase()(0):
			DoActions([
				_acts[0] << SetMemoryXEPD(self.epd, SetTo, 0, 0xFF),
				self.off.AddNumber(1)
			])
			EUDBreak()
		if EUDSwitchCase()(1):
			DoActions([
				_acts[1] << SetMemoryXEPD(self.epd, SetTo, 0, 0xFF00),
				self.off.AddNumber(1)
			])
			EUDBreak()
		if EUDSwitchCase()(2):
			DoActions([
				_acts[2] << SetMemoryXEPD(self.epd, SetTo, 0, 0xFF0000),
				self.off.AddNumber(1)
			])
			EUDBreak()
		if EUDSwitchCase()(3):
			DoActions([
				_acts[3] << SetMemoryXEPD(self.epd, SetTo, 0, 0xFF000000),
				self.epd.AddNumber(1), self.off.SetNumber(0)
			])
			EUDBreak()
		EUDEndSwitch()

	'''
	write_* functions do not write null byte
	'''
	@EUDMethod
	def write_str(self, srcptr):
		reader = EUDByteRW()
		reader.seekoffset(srcptr)

		if EUDInfLoop()():
			# read
			b = reader.read()

			# break
			EUDBreakIf(b == 0)

			# copy
			self.write(b)
		EUDEndInfLoop()

	@EUDMethod
	def write_strn(self, srcptr, n):
		reader = EUDByteRW()
		reader.seekoffset(srcptr)

		if EUDWhile()(n >= 1):
			# read
			b = reader.read()

			# break
			EUDBreakIf(b == 0)

			# copy
			self.write(b)
			n -= 1
		EUDEndWhile()

	@EUDMethod
	def write_strepd(self, srcepd):
		reader = EUDByteRW()
		reader.seekepd(srcepd)

		if EUDInfLoop()():
			# read
			b = reader.read()

			# break
			EUDBreakIf(b == 0)

			# copy
			self.write(b)
		EUDEndInfLoop()

	@EUDMethod
	def write_decimal(self, number):
		skipper = [Forward() for _ in range(9)]
		ch = [0] * 10

		# Get digits
		for i in range(10):
			number, ch[i] = f_div(number, 10)
			if i != 9:
				EUDJumpIf(number == 0, skipper[i])

		# print digits
		for i in range(9, -1, -1):
			if i != 9:
				skipper[i] << NextTrigger()
			self.write(ch[i] + ord('0'))

	@EUDMethod
	def write_hex(self, number):
		ch = [0] * 8

		self.write(ord('0'))
		self.write(ord('x'))

		# Get digits
		for i in range(8):
			number, ch[i] = f_div(number, 16)

		# print digits
		for i in range(7, -1, -1):
			if EUDIf()(ch[i] <= 9):
				self.write(ch[i] + ord('0'))
			if EUDElse()():
				self.write(ch[i] + (ord('A') - 10))
			EUDEndIf()

	@EUDMethod
	def write_binary(self, number):
		self.write(ord('0'))
		self.write(ord('b'))

		for i in range(31, -1, -1):
			if i in [23, 15, 7]:
				self.write(ord(' '))
			if EUDIf()(MemoryX(number.getValueAddr(), Exactly, 2**i, 2**i)):
				self.write(ord('1'))
			if EUDElse()():
				self.write(ord('0'))
			EUDEndIf()

	@EUDMethod
	def write_bytehex(self, number):
		ch = [0] * 2

		# Get digits
		for i in range(2):
			number, ch[i] = f_div(number, 16)

		# print digits
		for i in range(1, -1, -1):
			if EUDIf()(ch[i] <= 9):
				self.write(ch[i] + ord('0'))
			if EUDElse()():
				self.write(ch[i] + (ord('A') - 10))
			EUDEndIf()

	@EUDMethod
	def write_memoryTable(self, offset, cnt):
		reader = EUDByteRW()
		reader.seekoffset(offset)

		written = EUDVariable()
		written << 0
		if EUDInfLoop()():
			EUDBreakIf(cnt == 0)

			b = reader.read()

			self.write_bytehex(b)
			self.write_str(makeText(' '))

			DoActions(cnt.SubtractNumber(1))
		EUDEndInfLoop()
