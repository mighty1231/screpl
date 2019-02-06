from eudplib import *
from ...core.command import EUDCommand, registerCommand, _repl_commands
from ...core.referencetable import SearchTable
from ...core.encoder import ReadName, ArgEncoderPtr
from ..table.tables import (
	encoding_tables,
)
from ...utils import f_strcmp_ptrepd, EPDConstString
from ...view import (
	StaticView,
	TableView,
	tableDec_Command,
	tableDec_String,
	tableDec_StringDecimal
)

def registerBasicCmds():
	registerCommand("help", cmd_help)
	registerCommand("cmds", cmd_commands)
	registerCommand("tables", cmd_encoders)
	registerCommand("contents", cmd_contents)

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
	arg = EUDArray([
		EPDConstString('SC-REPL manual'),
		len(help_text)] + list(map(EPDConstString, help_text)))
	StaticView.OpenView(EPD(arg))

@EUDCommand([])
def cmd_commands():
	arg = EUDArray([
		EPDConstString("Commands"),
		EUDFuncPtr(2, 0)(tableDec_Command),
		EPD(_repl_commands)
	])
	TableView.OpenView(EPD(arg))

@EUDCommand([])
def cmd_encoders():
	arg = EUDArray([
		EPDConstString("List of encoders"),
		EUDFuncPtr(2, 0)(tableDec_String),
		EPD(encoding_tables)
	])
	TableView.OpenView(EPD(arg))

@EUDFunc
def _argEncEncoderName(offset, delim, ref_offset_epd, retval_epd):
	tmpbuf = Db(150)
	if EUDIf()(ReadName(offset, delim, ref_offset_epd, EPD(tmpbuf)) == 1):
		if EUDIf()(SearchTable(tmpbuf, EPD(encoding_tables), f_strcmp_ptrepd, retval_epd) == 1):
			EUDReturn(1)
		EUDEndIf()
	EUDEndIf()
	f_dwwrite_epd(ref_offset_epd, offset)
	EUDReturn(0)

@EUDCommand([ArgEncoderPtr(_argEncEncoderName)])
def cmd_contents(table_epd):
	'''
	see contents of table ex) contents(MapLocation)
	'''
	arg = EUDArray([
		EPDConstString("Contents"),
		EUDFuncPtr(2, 0)(tableDec_StringDecimal),
		0
	])
	arg[2] = table_epd
	TableView.OpenView(EPD(arg))
