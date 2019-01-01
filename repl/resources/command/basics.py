from eudplib import *
from ...utils import makeEPDTextArray
from ...core.command import EUDCommand
from ...core.table import SearchTable
from ...core.encoder import ReadName
from ..table.tables import (
	encoding_tables,
	repl_commands,
	RegisterCommand
)
from ...repl.board import Board
from ..table.itemdecoder import (
	decItem_Command,
	decItem_String,
	decItem_StringDecimal
)
from ...utils import makeText, makeEPDText, f_strcmp_ptrepd
from ...view import StaticView

def register_basiccmds():
	RegisterCommand("help", cmd_help)
	RegisterCommand("help2", cmd_help2)
	RegisterCommand("cmds", cmd_commands)
	RegisterCommand("tables", cmd_encoders)
	RegisterCommand("contents", cmd_contents)


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
	br = Board.GetInstance()
	br.SetTitle(makeText('SC-REPL Manual'))
	br.SetStaticContent(*makeEPDTextArray(help_text))
	br.SetMode(1)

@EUDCommand([])
def cmd_help2():
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
	inp = EUDArray([
		makeEPDText('SC-REPL manual'),
		len(help_text)] + list(map(makeEPDText, help_text)))
	StaticView.OpenView(EPD(inp))

@EUDCommand([])
def cmd_commands():
	br = Board.GetInstance()
	br.SetTitle(makeText("Commands"))
	br.SetContentWithTable_epd(EPD(repl_commands), decItem_Command)
	br.SetMode(1)

@EUDCommand([])
def cmd_encoders():
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
def cmd_contents(table_epd):
	'''
	see contents of table ex) contents(MapLocation)
	'''
	br = Board.GetInstance()
	br.SetTitle(makeText('List'))
	br.SetContentWithTable_epd(table_epd, decItem_StringDecimal)
	br.SetMode(1)
