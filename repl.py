from eudplib import *
from utils import *
from encoder import ReadName
import eudx
from board import Board

class REPL:
	def __init__(self, commands, keystate_callbacks = [], superuser = P1):
		self.epd, self.off = EUDCreateVariables(2)
		self.retval, self.errmsg_epd = EUDCreateVariables(2)
		self.rettext = Db(1024)

		self.offset = EUDVariable()
		self.ref_offset_epd = EPD(self.offset.getValueAddr())

		self.prev_txtPtr = EUDVariable(initval=10)

		self._cmds = commands
		self.cmds = EUDVArray(len(self._cmds))(self._cmds)

		from command import EUDCommandStruct
		self.cmds._basetype = EUDCommandStruct

		# superuser's name
		# assert isinstance(superuser, str), 'must be string'
		# self.prefix = makeText(superuser + ':')
		# self.prefixlen = len(superuser + ':')
		self.pid = EncodePlayer(superuser)
		self.prefix = Db(26)
		self.prefixlen = EUDVariable()
		f_strcpy(self.prefix, 0x57EEEB + 36*self.pid)
		self.prefixlen << f_strlen(0x57EEEB)


		# Previously stored key states
		# list of tuple: (keycode, callwhen, callback)
		# callwhen is one of fllowings
		#   OnKeyDown  : called once when key UP->DOWN
		#   OnKeyUp    : called once when key DOWN->UP
		#   OnKeyPress : called whenever key is pressed
		_keydict = {'F7': 0x76, 'F8': 0x77, 'F9': 0x78, 'ESC': 0x1B}
		self.keycodes = []
		self.keystate_callbacks = []
		for keycode, callwhen, callback in keystate_callbacks:
			keycode = _keydict.get(keycode, keycode)
			if keycode not in self.keycodes:
				self.keycodes.append(keycode)
			self.keystate_callbacks.append((keycode, callwhen, callback))
		assert len(self.keycodes) <= 32
		self.prev_keystate = EUDVariable()

	def update_keystate(self):
		cur_keystate = EUDVariable()

		# update current keystate
		for i, offset in enumerate(self.keycodes):
			m = 256 ** (offset % 4)
			n = 2 ** (offset % 32)
			RawTrigger(
				conditions = eudx.MemoryX(0x596A18 + offset, Exactly, 0, m),
				actions = eudx.SetMemoryX(
					cur_keystate.getValueAddr(),
					SetTo, 0, 2**i
				)
			)
			RawTrigger(
				conditions = eudx.MemoryX(0x596A18 + offset, Exactly, m, m),
				actions = eudx.SetMemoryX(
					cur_keystate.getValueAddr(),
					SetTo, 2**i, 2**i
				)
			)

		# call functions
		for keycode, callwhen, callback in self.keystate_callbacks:
			pos = 2 ** self.keycodes.index(keycode)
			if callwhen == 'OnKeyDown':
				if EUDIf()([
							eudx.MemoryX(self.prev_keystate.getValueAddr(),
								Exactly, 0, pos),
							eudx.MemoryX(cur_keystate.getValueAddr(),
								Exactly, pos, pos),
						]):
					callback()
				EUDEndIf()
			elif callwhen == 'OnKeyUp':
				if EUDIf()([
							eudx.MemoryX(self.prev_keystate.getValueAddr(),
								Exactly, pos, pos),
							eudx.MemoryX(cur_keystate.getValueAddr(),
								Exactly, 0, pos),
						]):
					callback()
				EUDEndIf()
			elif callwhen == 'OnKeyPress':
				if EUDIf()(
							eudx.MemoryX(cur_keystate.getValueAddr(),
								Exactly, pos, pos)
						):
					callback()
				EUDEndIf()

		# update previous value
		self.prev_keystate << cur_keystate

	@EUDMethod
	def _execute_command(self, offset):
		br = Board.GetInstance()
		br.REPLWriteInput(offset)
		offset_cpy = EUDVariable()
		offset_cpy << offset
		ref_offset_epd = EPD(offset.getValueAddr())

		# Read function first
		if EUDIf()(ReadName(offset, ord('('), ref_offset_epd, EPD(self.rettext)) == 1):
			cmds_cnt = len(self._cmds)

			func_idx = EUDVariable()
			func_idx << 0

			argidx = EUDVariable()
			argidx << 0
			if EUDWhile()(func_idx <= cmds_cnt - 1):

				# Search for available functions
				if EUDIf()(f_strcmp2(self.rettext, self.cmds[func_idx].cmdname) == 0):
					if EUDIf()(self.cmds[func_idx].cmdptr(
							offset, br.repl_outputEPDPtr, br._dbgbug_epd) == 1):
						# br.REPLWriteOutput(makeText('Success!'))
						pass
					if EUDElse()():
						# br.REPLWriteOutput(makeText('Failed!'))
						pass
					EUDEndIf()
					br.REPLCompleteEval()
					EUDReturn()
				EUDEndIf()
				func_idx += 1
			EUDEndWhile()
			br.REPLWriteOutput(makeText('\x06Failed to read function name'))
		EUDEndIf()
		br.REPLCompleteEval()

	@EUDMethod
	def execute(self):
		'''
		Main part of REPL
		'''
		self.update_keystate()

		if EUDIf()(Memory(0x640B58, Exactly, self.prev_txtPtr)):
			EUDReturn()
		EUDEndIf()

		cur_txtPtr = f_dwread_epd(EPD(0x640B58))
		i = EUDVariable()
		i << self.prev_txtPtr
		chat_off = 0x640B60 + 218 * i

		_nextline = Forward()
		if EUDInfLoop()():
			EUDBreakIf(i == cur_txtPtr)

			if EUDIf()(f_memcmp(chat_off, self.prefix, self.prefixlen) == 0):

				self._execute_command(chat_off + (self.prefixlen + 2)) # 2 from (colorcode, spacebar)

			EUDEndIf()
			if EUDIf()(i == 10):
				i << 0
				chat_off << 0x640B60
			if EUDElse()():
				i += 1
				chat_off += 218
			EUDEndIf()
		EUDEndInfLoop()

		self.prev_txtPtr << cur_txtPtr
