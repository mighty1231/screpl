from eudplib import *
from utils import *
from command import *

def testCmdPtr():
	from command import EUDCommand, EUDCommandPtr
	from constenc import argEncNumber, argEncModifier

	@EUDCommand([argEncNumber, argEncModifier, argEncNumber])
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

class eight(EUDStruct):
	_fields_ = ['a%d' % i for i in range(8)]

def testva2s():
	v = EUDVArray(8)([i for i in range(8)])
	a = eight.cast(v)
	f_simpleprint(a.a1, a.a2, a.a3, a.a4, a.a5, a.a6, a.a7)

	b = EUDVariable()

	b << v
	f_simpleprint(v, a.a2.getValueAddr(), a.a3.getValueAddr(), b.getValueAddr(), b, f_dwread(b))

def testLazy():
	from table import ReferenceTable, SearchTable
	@EUDFunc
	def compareInt(k, v):
		f_simpleprint('compare', k, v)
		if EUDIf()(k == v):
			EUDReturn(1)
		EUDEndIf()
		EUDReturn(0)

	rt = ReferenceTable()
	f = ReferenceTable([(1, 2), (3, 4)], [(rt, 2)])

	ret = EUDVariable()
	# f_simpleprint(SearchTable(3, EPD(f), compareInt, EPD(ret.getValueAddr())), ret)
	f_simpleprint(SearchTable(3, EPD(f), compareInt, EPD(ret.getValueAddr())), ret)

@EUDFunc
def main():
	if EUDInfLoop()():
		testLazy()
		EUDDoEvents()
	EUDEndInfLoop()

from config import outfname
LoadMap("base.scx")
SaveMap(outfname, main)

