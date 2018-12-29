from eudplib import *
from utils import *
from encoder import ReadName
from board import Board
from command import EUDCommandStruct

class REPL:
	def __init__(self, commands, keystate_callbacks = [], superuser = P1):
		self.rettext = Db(1024)
		self.prev_txtPtr = EUDVariable(initval=10)

		self.cmds = EUDArray(commands)
		self.cmdn = len(commands)

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
		br = Board.GetInstance()
		br.REPLWriteInput(offset)
		offset_cpy = EUDVariable()
		offset_cpy << offset
		ref_offset_epd = EPD(offset.getValueAddr())

		# Read function first
		if EUDIf()(ReadName(offset, ord('('), ref_offset_epd, EPD(self.rettext)) == 1):
			func_idx = EUDVariable()
			func_idx << 0

			argidx = EUDVariable()
			argidx << 0
			if EUDWhile()(func_idx <= self.cmdn - 1):

				# Search for available functions
				_f = EUDCommandStruct.cast(self.cmds[func_idx])
				if EUDIf()(f_strcmp2(self.rettext, _f.cmdname) == 0):
					if EUDIf()(_f.cmdptr(
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

def cmd_basics():
	from cmd_basics import (
		cmd_help, 
		cmd_memoryview,
		cmd_memoryview_epd,
		cmd_dwread,
		cmd_wread,
		cmd_bread,
		cmd_dwwrite,
		cmd_wwrite,
		cmd_bwrite,
	)
	commands = []
	commands.append(EUDCommandStruct('help', cmd_help))
	commands.append(EUDCommandStruct('mv', cmd_memoryview))
	commands.append(EUDCommandStruct('mvepd', cmd_memoryview_epd))
	commands.append(EUDCommandStruct('dwread', cmd_dwread))
	commands.append(EUDCommandStruct('wread', cmd_wread))
	commands.append(EUDCommandStruct('bread', cmd_bread))
	commands.append(EUDCommandStruct('dwwrite', cmd_dwwrite))
	commands.append(EUDCommandStruct('wwrite', cmd_wwrite))
	commands.append(EUDCommandStruct('bwrite', cmd_bwrite))
	return commands

_commands = []
def onPluginStart():
	global _commands
	from table import table_init
	from cmd_conditions import cmdstruct_all_conditions
	from cmd_actions import cmdstruct_all_actions
	_commands = cmd_basics()
	_commands += cmdstruct_all_conditions()
	_commands += cmdstruct_all_actions()

	# table_init should be called after all table initialized
	cmd_listTable, cmd_listTableContents = table_init()
	_commands.append(EUDCommandStruct('list_tables', cmd_listTable))
	_commands.append(EUDCommandStruct('tb_cons', cmd_listTableContents))

	# from ipc import make_db
	# make_db()

def beforeTriggerExec():
	# Turbo
	DoActions(SetDeaths(203151, SetTo, 1, 0))
	from repl import REPL
	from board import Board
	global _commands

	def SetPrevPage():
		br = Board.GetInstance()
		br.SetPrevPage()
		br.UpdatePage()

	def SetNextPage():
		br = Board.GetInstance()	
		br.SetNextPage()
		br.UpdatePage()

	def SetREPLPage():
		br = Board.GetInstance()
		br.SetMode(0)

	display = EUDVariable(1)
	def ToggleDisplay():
		DoActions(SetMemoryX(display.getValueAddr(), Add, 1, 1))

	key_callbacks = [
		('F7', 'OnKeyDown', SetPrevPage),
		('F8', 'OnKeyDown', SetNextPage),
		('F9', 'OnKeyDown', ToggleDisplay),
		('ESC', 'OnKeyDown', SetREPLPage),
	]
	from table import _table_list, _table_of_table, _var_list, vartrace_init 

	_var_list.append(('table of table', _table_of_table))
	cmd_vartrace = vartrace_init()
	_commands.append(EUDCommandStruct('vartrace', cmd_vartrace))

	cr = REPL(_commands, key_callbacks, superuser = P1)
	cr.execute()
	br = Board.GetInstance()
	if EUDIf()(display == 1):
		br.Display(P1)
	EUDEndIf()
