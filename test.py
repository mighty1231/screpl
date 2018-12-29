from eudplib import *
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