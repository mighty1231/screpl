from eudplib import *
from table import ReferenceTable, SearchTable
from utils import *
from command import EUDCommand

_objtable = ReferenceTable(key_f=makeEPDText)

def traceObject(name, var):
	_objtable.AddPair(name, var)

@EUDCommand([])
def cmd_objtrace():

	from board import Board
	br = Board.GetInstance()
	br.SetTitle(makeText("Objects"))
	br.SetContentWithTbName_epd(EPD(_objtable))
	br.SetMode(1)


def register_objtrace():
	global _objtable
	from repl import RegisterCommand
	RegisterCommand('objtrace', cmd_objtrace)
