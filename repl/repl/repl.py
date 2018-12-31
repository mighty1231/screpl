from eudplib import *
from ..utils import makeText
from ..utils.utils import f_strlen
from ..core.command import runCommand
from .board import Board
from ..resources.table.tables import repl_commands
from ..resources.command.basics import register_basiccmds
from ..resources.command.conditions import register_all_conditioncmds
from ..resources.command.actions import register_all_actioncmds
from ..resources.command.utils import register_utilcmds

_repl = None

class REPL:
	def __init__(self, superuser = P1):
		global _repl 
		assert _repl == None, "REPL instance should be unique"
		_repl = self

		self.rettext = Db(1024)
		self.prev_txtPtr = EUDVariable(initval=10)
		self.display = EUDVariable(1)

		# superuser's name
		# assert isinstance(superuser, str), 'must be string'
		# self.prefix = makeText(superuser + ':')
		# self.prefixlen = len(superuser + ':')
		self.playerId = EncodePlayer(superuser)
		assert 0 <= self.playerId < 8, "Superuser should be one of P1 ~ P8"
		self.prefix = Db(26)
		self.prefixlen = EUDVariable()
		self.board = Board.GetInstance()

		# these registering functions are python-functions
		register_basiccmds()
		register_utilcmds()
		register_all_conditioncmds()
		register_all_actioncmds()

		# Keystate functions
		def SetPrevPage():
			self.board.SetPrevPage()
			self.board.UpdatePage()

		def SetNextPage():
			self.board.SetNextPage()
			self.board.UpdatePage()

		def SetREPLPage():
			self.board.SetMode(0)

		def ToggleDisplay():
			DoActions(SetMemoryX(self.display.getValueAddr(), Add, 1, 1))

		keystate_callbacks = [
			('F7', 'OnKeyDown', SetPrevPage),
			('F8', 'OnKeyDown', SetNextPage),
			('F9', 'OnKeyDown', ToggleDisplay),
			('ESC', 'OnKeyDown', SetREPLPage),
		]

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
				conditions = MemoryX(0x596A18 + offset, Exactly, 0, m),
				actions = SetMemoryX(
					cur_keystate.getValueAddr(),
					SetTo, 0, 2**i
				)
			)
			RawTrigger(
				conditions = MemoryX(0x596A18 + offset, Exactly, m, m),
				actions = SetMemoryX(
					cur_keystate.getValueAddr(),
					SetTo, 2**i, 2**i
				)
			)

		# call functions
		for keycode, callwhen, callback in self.keystate_callbacks:
			pos = 2 ** self.keycodes.index(keycode)
			if callwhen == 'OnKeyDown':
				if EUDIf()([
							MemoryX(self.prev_keystate.getValueAddr(),
								Exactly, 0, pos),
							MemoryX(cur_keystate.getValueAddr(),
								Exactly, pos, pos),
						]):
					callback()
				EUDEndIf()
			elif callwhen == 'OnKeyUp':
				if EUDIf()([
							MemoryX(self.prev_keystate.getValueAddr(),
								Exactly, pos, pos),
							MemoryX(cur_keystate.getValueAddr(),
								Exactly, 0, pos),
						]):
					callback()
				EUDEndIf()
			elif callwhen == 'OnKeyPress':
				if EUDIf()(
							MemoryX(cur_keystate.getValueAddr(),
								Exactly, pos, pos)
						):
					callback()
				EUDEndIf()

		# update previous value
		self.prev_keystate << cur_keystate

	@EUDMethod
	def _execute_command(self, offset):
		self.board.REPLWriteInput(offset)
		runCommand(offset, EPD(repl_commands), self.board.repl_outputEPDPtr)
		self.board.REPLCompleteEval()

	@EUDMethod
	def execute(self):
		'''
		Main part of REPL
		'''
		# key callbacks
		self.update_keystate()

		# Check whether user typed nothing
		do_display = Forward()
		if EUDIf()(Memory(0x640B58, Exactly, self.prev_txtPtr)):
			EUDJump(do_display)
		EUDEndIf()

		# copy P1's name
		f_strcpy(self.prefix, 0x57EEEB + 36*self.playerId)
		self.prefixlen << f_strlen(0x57EEEB)

		cur_txtPtr = f_dwread_epd(EPD(0x640B58))
		i = EUDVariable()
		i << self.prev_txtPtr
		chat_off = 0x640B60 + 218 * i

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

		do_display << NextTrigger()
		if EUDIf()(self.display == 1):
			self.board.Display(self.playerId)
		EUDEndIf()
