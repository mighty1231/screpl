from eudplib import *
from utils import *
from command import EUDCommand
from board import Board
from tables import RegisterCommand
from encoder import ReadName
from table import (
    SearchTable,
    decItem_String,
    decItem_StringDecimal,
    decItem_StringHex
)
from tables import encoding_tables, traced_objects, repl_commands

def register_cmds():
	RegisterCommand("cmds", cmd_commands)
	RegisterCommand("tables", cmd_listEncoders)
	RegisterCommand("contents", cmd_printEncoder)
	RegisterCommand('objtrace', cmd_objtrace)

@EUDCommand([])
def cmd_listEncoders():
	br = Board.GetInstance()
	br.SetTitle(makeText('List of encoders'))
	br.SetContentWithTable_epd(EPD(encoding_tables), decItem_String)
	br.SetMode(1)

@EUDFunc
def argEncEncoderName(offset, delim, ref_offset_epd, retval_epd):
	tmpbuf = Db(150)
	if EUDIf()(ReadName(offset, delim, ref_offset_epd, EPD(tmpbuf)) == 1):
		if EUDIf()(SearchTable(tmpbuf, EPD(encoding_tables), f_strcmp_ptrepd, retval_epd) == 1):
			EUDReturn(1)
		EUDEndIf()
	EUDEndIf()
	f_dwwrite_epd(ref_offset_epd, offset)
	EUDReturn(0)

@EUDCommand([argEncEncoderName])
def cmd_printEncoder(table_epd):
	br = Board.GetInstance()
	br.SetTitle(makeText('List'))
	br.SetContentWithTable_epd(table_epd, decItem_StringDecimal)
	br.SetMode(1)

@EUDCommand([])
def cmd_objtrace():
	br = Board.GetInstance()
	br.SetTitle(makeText("Objects"))
	br.SetContentWithTable_epd(EPD(traced_objects), decItem_StringHex)
	br.SetMode(1)

@EUDCommand([])
def cmd_commands():
	br = Board.GetInstance()
	br.SetTitle(makeText("Commands"))
	br.SetContentWithTable_epd(EPD(repl_commands), decItem_String)
	br.SetMode(1)
