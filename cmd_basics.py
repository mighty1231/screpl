from eudplib import *
from utils import *
from command import EUDCommand
from constenc import (
	arg_EncodeNumber,
	arg_EncodeCount,
	arg_EncodeModifier,
	arg_EncodeAllyStatus,
	arg_EncodeComparison,
	arg_EncodeOrder,
	arg_EncodePlayer,
	arg_EncodePropState,
	arg_EncodeResource,
	arg_EncodeScore,
	arg_EncodeSwitchAction,
	arg_EncodeSwitchState,
)
from strenc import (
	arg_EncodeUnit,
	arg_EncodeLocation,
	arg_EncodeAIScript,
	arg_EncodeSwitch,
	arg_EncodeString,
)
from decoder import (
	ret_DecodeBool,
	ret_DecodeDecimal,
	ret_DecodeHex,
	ret_DecodeBinary,
)

# Basic commands
@EUDCommand([])
def cmd_help():
	help_text = [
		'\x13SC-REPL ver 0.1',
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
		'list() - See list of all functions (To be developed)',
		'listtb() - See list of registered tables',
		'listtbcon(table) - See list of table contents',
		'',
	]
	from board import Board
	br = Board.GetInstance()
	br.SetTitle(makeText('SC-REPL Manual'))
	br.SetStaticContent(*makeTextEPDArray(help_text))
	br.SetMode(1)

@EUDCommand([arg_EncodeNumber])
def cmd_memoryview(offset):
	from board import Board
	bufs = EUDArray([EPD(Db(300)) for i in range(8)])
	writer = EUDByteRW()
	reader = EUDByteRW()
	reader.seekoffset(offset)

	i = EUDVariable()
	i << 0
	if EUDWhile()(i < 16):
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

@EUDCommand([arg_EncodeNumber])
def cmd_memoryview_epd(epd):
	offset = f_epd2ptr(epd)

	from board import Board
	bufs = EUDArray([EPD(Db(300)) for i in range(8)])
	writer = EUDByteRW()
	reader = EUDByteRW()
	reader.seekoffset(offset)

	i = EUDVariable()
	i << 0
	if EUDWhile()(i < 16):
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
@EUDCommand([arg_EncodeNumber, arg_EncodeNumber], \
		[ret_DecodeDecimal, ret_DecodeDecimal])
def cmd_div(a, b):
	c, d = f_div(a, b)
	EUDReturn([c, d])

@EUDCommand([arg_EncodeNumber], [ret_DecodeDecimal, ret_DecodeHex, ret_DecodeBinary])
def cmd_dwread(ptr):
	val = f_dwread(ptr)
	EUDReturn([val, val, val])

@EUDCommand([arg_EncodeNumber], [ret_DecodeDecimal, ret_DecodeHex, ret_DecodeBinary])
def cmd_wread(ptr):
	val = f_wread(ptr)
	EUDReturn([val, val, val])

@EUDCommand([arg_EncodeNumber], [ret_DecodeDecimal, ret_DecodeHex, ret_DecodeBinary])
def cmd_bread(ptr):
	val = f_bread(ptr)
	EUDReturn([val, val, val])

@EUDCommand([arg_EncodeNumber, arg_EncodeNumber])
def cmd_dwwrite(ptr, val):
	f_dwwrite(ptr, val)

@EUDCommand([arg_EncodeNumber, arg_EncodeNumber])
def cmd_wwrite(ptr, val):
	f_wwrite(ptr, val)

@EUDCommand([arg_EncodeNumber, arg_EncodeNumber])
def cmd_bwrite(ptr, val):
	f_bwrite(ptr, val)
