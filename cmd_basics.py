from eudplib import *
from utils import *
from command import EUDCommand
from enc_const import (
	argEncNumber,
	argEncCount,
	argEncModifier,
	argEncAllyStatus,
	argEncComparison,
	argEncOrder,
	argEncPlayer,
	argEncPropState,
	argEncResource,
	argEncScore,
	argEncSwitchAction,
	argEncSwitchState,
)
from enc_str import (
	argEncUnit,
	argEncLocation,
	argEncAIScript,
	argEncSwitch,
	argEncString,
)
from decoder import (
	retDecBool,
	retDecDecimal,
	retDecHex,
	retDecBinary,
)

def register_all_basiccmds():
	from tables import RegisterCommand

	RegisterCommand('help', cmd_help)
	RegisterCommand('mv', cmd_memoryview)
	RegisterCommand('mvepd', cmd_memoryview_epd)
	RegisterCommand('dwread', cmd_dwread)
	RegisterCommand('wread', cmd_wread)
	RegisterCommand('bread', cmd_bread)
	RegisterCommand('dwwrite', cmd_dwwrite)
	RegisterCommand('wwrite', cmd_wwrite)
	RegisterCommand('bwrite', cmd_bwrite)

# Basic commands
@EUDCommand([])
def cmd_help():
	help_text = [
		'\x13SC-REPL ver 0.2',
		'\x13Made by sixthMeat',
		'',
		'Key Inputs',
		'- F7: Search previous page',
		'- F8: Search next page',
		'- F9: Toggle display',
		'- Esc: Get back into REPL',
		'',
		'build in functions',
		'help() - See manual',
		'cmds() - See list of all commands',
		'tables() - See list of encoder tables (Used in trigger)',
		'contents(table) - See contents in encoder tables',
		'',
	]
	from board import Board
	br = Board.GetInstance()
	br.SetTitle(makeText('SC-REPL Manual'))
	br.SetStaticContent(*makeTextEPDArray(help_text))
	br.SetMode(1)

@EUDCommand([argEncNumber])
def cmd_memoryview(offset):
	from board import Board
	bufs = EUDArray([EPD(Db(300)) for i in range(8)])
	writer = EUDByteRW()
	reader = EUDByteRW()
	reader.seekoffset(offset)

	i = EUDVariable()
	i << 0
	if EUDWhile()(i < 8):
		writer.seekepd(bufs[i])
		writer.write_hex(offset)
		writer.write_str(makeText(': '))

		if EUDLoopN()(16):
			writer.write_bytehex(reader.read())
			writer.write(ord(' '))
		EUDEndLoopN()
		writer.write_str(makeText(' | '))
		writer.write_strn(offset, 16)
		writer.write(0)

		offset += 16
		i += 1
	EUDEndWhile()

	br = Board.GetInstance()
	br.SetTitle(makeText('Memory View'))
	br.SetStaticContent(bufs, 8)
	br.SetMode(1)

@EUDCommand([argEncNumber])
def cmd_memoryview_epd(epd):
	offset = f_epd2ptr(epd)

	from board import Board
	bufs = EUDArray([EPD(Db(300)) for i in range(8)])
	writer = EUDByteRW()
	reader = EUDByteRW()
	reader.seekoffset(offset)

	i = EUDVariable()
	i << 0
	if EUDWhile()(i < 8):
		writer.seekepd(bufs[i])
		writer.write_hex(offset)
		writer.write_str(makeText(': '))

		if EUDLoopN()(16):
			writer.write_bytehex(reader.read())
			writer.write(ord(' '))
		EUDEndLoopN()
		writer.write_str(makeText(' | '))
		writer.write_strn(offset, 16)
		writer.write(0)

		offset += 16
		i += 1
	EUDEndWhile()

	br = Board.GetInstance()
	br.SetTitle(makeText('Memory View'))
	br.SetStaticContent(bufs, 8)
	br.SetMode(1)

# Example
@EUDCommand([argEncNumber, argEncNumber], \
		[retDecDecimal, retDecDecimal])
def cmd_div(a, b):
	c, d = f_div(a, b)
	EUDReturn([c, d])

@EUDCommand([argEncNumber], [retDecDecimal, retDecHex, retDecBinary])
def cmd_dwread(ptr):
	val = f_dwread(ptr)
	EUDReturn([val, val, val])

@EUDCommand([argEncNumber], [retDecDecimal, retDecHex, retDecBinary])
def cmd_wread(ptr):
	val = f_wread(ptr)
	EUDReturn([val, val, val])

@EUDCommand([argEncNumber], [retDecDecimal, retDecHex, retDecBinary])
def cmd_bread(ptr):
	val = f_bread(ptr)
	EUDReturn([val, val, val])

@EUDCommand([argEncNumber, argEncNumber])
def cmd_dwwrite(ptr, val):
	f_dwwrite(ptr, val)

@EUDCommand([argEncNumber, argEncNumber])
def cmd_wwrite(ptr, val):
	f_wwrite(ptr, val)

@EUDCommand([argEncNumber, argEncNumber])
def cmd_bwrite(ptr, val):
	f_bwrite(ptr, val)
