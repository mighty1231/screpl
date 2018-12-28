from eudplib import *
import customText as ct
from utils import *
from command import *


def testCmdPtr():
	from command import EUDCommand, EUDCommandPtr
	from constenc import arg_EncodeNumber, arg_EncodeModifier

	@EUDCommand([arg_EncodeNumber, arg_EncodeModifier, arg_EncodeNumber])
	def cmd_SetMemory2(memory, modifier, value):
		DoActions(SetMemory(memory, modifier, value))

	EUDCommandPtr(cmd_SetMemory2)(makeText('0x57F0F0, SetTo, 1)'))
	EUDCommandPtr(cmd_SetMemory2)(makeText('0x57F0F0, Add, 341)'))

def testReadName():
	from encoder import ReadName
	db = makeText('abcdefgh_b,')
	ret = DBString(150)
	ptr = EUDVariable()
	ct.f_printAll(readn, ReadName(db, ord(','), EPD(ptr.getValueAddr()), EPD(ret)+1))
	a = DBString(20)
	f_dbstr_addstr(a, ret+4)
	a.Display()

def cmd_tables():
	from table import cmd_listTable, cmd_listTableContents
	commands = []

	return commands

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

	from ipc import make_db
	make_db()

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
		DoActions(eudx.SetMemoryX(display.getValueAddr(), Add, 1, 1))

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
