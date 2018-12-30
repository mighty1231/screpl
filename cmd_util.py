from eudplib import *
from utils import *
from command import EUDCommand
from board import Board
from tables import RegisterCommand, traced_objects
from table import decItem_StringHex
from enc_const import argEncNumber
from decoder import retDecDecimal, retDecHex, retDecBinary

def register_utilcmds():
	RegisterCommand('mv', cmd_memoryview)
	RegisterCommand('mvepd', cmd_memoryview_epd)
	RegisterCommand('dwread', cmd_dwread)
	RegisterCommand('wread', cmd_wread)
	RegisterCommand('bread', cmd_bread)
	RegisterCommand('dwwrite', cmd_dwwrite)
	RegisterCommand('wwrite', cmd_wwrite)
	RegisterCommand('bwrite', cmd_bwrite)
	RegisterCommand('objtrace', cmd_objtrace)

@EUDCommand([])
def cmd_objtrace():
	'''
	get address table of marked EUDObjects with RegisterTraceObject
	'''
	br = Board.GetInstance()
	br.SetTitle(makeText("Objects"))
	br.SetContentWithTable_epd(EPD(traced_objects), decItem_StringHex)
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
