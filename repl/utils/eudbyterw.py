from eudplib import *
from .conststring import EPDConstString

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
			self.write_str(ConstString(' '))

			DoActions(cnt.SubtractNumber(1))
		EUDEndInfLoop()

	def write_f(self, fmt, *args):
		'''
		Parse formatted string with python (not in-game)
		  and write it with EUDVariable or ConstExpr

		CAUTION: This does NOT make null end

		Available formats:
		 - %H: Write hexadecimal value starts with 0x
		 - %D: Write decimal value
		 - %S: Write string with ptr
		 - %E: Write string with epd
		 - %C: Write single character

		Write %% to represent %
		'''
		# parse format and compare its argument count
		#   with args
		# ITEMS: list of tuples (format, arg)
		items = []
		pos = 0
		argidx = 0
		while pos < len(fmt):
			if '%' not in fmt[pos:]:
				items.append(('const', fmt[pos:]))
				break
			fmpos = fmt[pos:].index('%')

			# push conststr before %
			if fmpos > 0:
				items.append(('const', fmt[pos:pos+fmpos]))
				pos += fmpos

			# get argument
			if argidx >= len(args):
				raise RuntimeError("Mismatch on count between " \
					"format string and argument counton write_f")
			curarg = args[argidx]
			if fmt[pos+1] == '%':
				items.append(('const', '%'))
			elif fmt[pos+1] == 'H':
				items.append(('H', curarg))
				argidx += 1
			elif fmt[pos+1] == 'D':
				items.append(('D', curarg))
				argidx += 1
			elif fmt[pos+1] == 'S':
				items.append(('S', curarg))
				argidx += 1
			elif fmt[pos+1] == 'E':
				items.append(('E', curarg))
				argidx += 1
			elif fmt[pos+1] == 'C':
				items.append(('C', curarg))
				argidx += 1
			else:
				print(fmt[pos:])
				raise RuntimeError("Unable to parse {}".format(fmt))
			pos += 2
		if len(args) != argidx:
			raise RuntimeError("Mismatch on count between " \
				"format string and argument counton write_f")

		# Due to %%, several const string could be
		#   located consecutively, so merge it
		merged_items = [items[0]]
		for fm, arg in items[1:]:
			if fm == 'const' and merged_items[-1][0] == 'const':
				merged_items[-1] = (merged_items[-1][0],
						merged_items[-1][1] + arg)
			else:
				merged_items.append((fm, arg))

		# Short constants are written with bytes, otherwise use EPDConstString
		for fm, arg in merged_items:
			if fm == 'const':
				if len(arg) == 1:
					self.write(ord(arg))
				else:
					self.write_strepd(EPDConstString(arg))
			elif fm == 'H':
				self.write_hex(arg)
			elif fm == 'D':
				self.write_decimal(arg)
			elif fm == 'S':
				self.write_str(arg)
			elif fm == 'E':
				self.write_strepd(arg)
			elif fm == 'C':
				self.write(arg)
