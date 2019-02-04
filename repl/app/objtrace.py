from eudplib import *
from ..core.referencetable import ReferenceTable
from ..core.command import EUDCommand, registerCommand
from ..utils import EPDConstString
from ..view import TableView, tableDec_StringHex

traced_objects = ReferenceTable(key_f=EPDConstString)

def registerObjTrace():
	@EUDCommand([])
	def cmd_objtrace():
		'''
		get address table of traced EUDObjects
		'''
		arg = EUDArray([
			EPDConstString("Objects"),
			EUDFuncPtr(2, 0)(tableDec_StringHex),
			EPD(traced_objects)
		])
		TableView.OpenView(EPD(arg))

	registerCommand('objtrace', cmd_objtrace)

def traceObject(name, var):
	traced_objects.AddPair(name, var)
