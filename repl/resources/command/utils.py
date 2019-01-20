from eudplib import *
from ...utils import EUDByteRW, EPDConstString
from ...core.command import EUDCommand
from ...core.decoder import retDecDecimal, retDecHex, retDecBinary
from ..table.tables import RegisterCommand, traced_objects, traced_variables
from ..encoder.const import (
	argEncNumber,
	argEncPlayer,
	argEncResource,
	argEncScore
)
from ..encoder.str import (
	argEncUnit,
	argEncLocation,
)
from ...view import (
	StaticView,
	TableView,
	VariableView,
	tableDec_StringHex,
	UnitArrayView,
	TriggerView
)

def register_utilcmds():
	# EUDVariable
	RegisterCommand('mul', cmd_mul)
	RegisterCommand('div', cmd_div)

	# Memory manipulation
	RegisterCommand('dwread', cmd_dwread)
	RegisterCommand('wread', cmd_wread)
	RegisterCommand('bread', cmd_bread)
	RegisterCommand('dwwrite', cmd_dwwrite)
	RegisterCommand('wwrite', cmd_wwrite)
	RegisterCommand('bwrite', cmd_bwrite)
	RegisterCommand('memcpy', cmd_memcpy)
	RegisterCommand('strcpy', cmd_strcpy)

	# Memory view
	RegisterCommand('mv', cmd_memoryview)

	# Special
	RegisterCommand('objtrace', cmd_objtrace)
	RegisterCommand('vartrace', cmd_vartrace)

	# Unit
	RegisterCommand('units', cmd_unitarrayview)

	# Trigger
	RegisterCommand('tv', cmd_triggerview)

	# Extended Conditions
	RegisterCommand('exCountdownTimer', cmd_ExCountdownTimer)
	RegisterCommand('exCommand', cmd_ExCommand)
	RegisterCommand('exBring', cmd_ExBring)
	RegisterCommand('exAccumulate', cmd_ExAccumulate)
	RegisterCommand('exKills', cmd_ExKills)
	RegisterCommand('exElapsedTime', cmd_ExElapsedTime)
	RegisterCommand('exOpponents', cmd_ExOpponents)
	RegisterCommand('exDeaths', cmd_ExDeaths)
	RegisterCommand('exScore', cmd_ExScore)

@EUDCommand([argEncNumber, argEncNumber], \
		[retDecDecimal, retDecHex])
def cmd_mul(a, b):
	v = f_mul(a, b)
	EUDReturn([v, v])

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

@EUDCommand([argEncNumber, argEncNumber, argEncNumber])
def cmd_memcpy(dst, src, copylen):
	f_memcpy(dst, src, copylen)

@EUDCommand([argEncNumber, argEncNumber])
def cmd_strcpy(dst, src):
	f_strcpy(dst, src)

@EUDCommand([argEncNumber])
def cmd_memoryview(offset):
	args = EUDArray([EPDConstString('Memory View'), 8] \
		+ [EPD(Db(300)) for i in range(8)])
	writer = EUDByteRW()
	reader = EUDByteRW()
	reader.seekoffset(offset)

	i = EUDVariable()
	i << 2
	if EUDWhile()(i < 8+2):
		writer.seekepd(args[i])
		writer.write_hex(offset)
		writer.write_strepd(EPDConstString(': '))

		if EUDLoopN()(16):
			writer.write_bytehex(reader.read())
			writer.write(ord(' '))
		EUDEndLoopN()
		writer.write_strepd(EPDConstString(' | '))
		writer.write_strn(offset, 16)
		writer.write(0)

		offset += 16
		i += 1
	EUDEndWhile()
	StaticView.OpenView(EPD(args))

@EUDCommand([])
def cmd_objtrace():
	'''
	get address table of marked EUDObjects with RegisterTraceObject
	'''
	arg = EUDArray([
		EPDConstString("Objects"),
		EUDFuncPtr(2, 0)(tableDec_StringHex),
		EPD(traced_objects)
	])
	TableView.OpenView(EPD(arg))

@EUDCommand([])
def cmd_vartrace():
	'''
	get address table of marked EUDObjects with RegisterTraceObject
	'''
	VariableView.OpenView(EPD(traced_variables))

@EUDCommand([])
def cmd_unitarrayview():
	'''
	view for CUnit array
	'''
	UnitArrayView.OpenView(0)

@EUDCommand([argEncNumber])
def cmd_triggerview(ptr):
	'''
	view for trigger
	'''
	TriggerView.OpenView(ptr)

@EUDCommand([], [retDecDecimal])
def cmd_ExCountdownTimer():
	'''
	Get x satisfies CountdownTimer(Exactly, x)
	'''
	v = EUDBinaryMax(lambda x:CountdownTimer(AtLeast, x))
	EUDReturn(v)

@EUDCommand([argEncPlayer, argEncUnit], [retDecDecimal])
def cmd_ExCommand(Player, Unit):
	'''
	Player, Unit-> Get x satisfies Command(Player, Exactly, x, Unit)
	'''
	v = EUDBinaryMax(lambda x:Command(Player, AtLeast, x, Unit))
	EUDReturn(v)

@EUDCommand([argEncPlayer, argEncUnit, argEncLocation], [retDecDecimal])
def cmd_ExBring(Player, Unit, Location):
	'''
	Player, Unit, Location -> Get x satisfies Bring(Player, Exactly, x, Unit, Location)
	'''
	v = EUDBinaryMax(lambda x:Bring(Player, AtLeast, x, Unit, Location))
	EUDReturn(v)

@EUDCommand([argEncPlayer, argEncResource], [retDecDecimal])
def cmd_ExAccumulate(Player, ResourceType):
	'''
	Player, ResourceType -> Get x satisfies Accumulate(Player, Exactly, x, ResourceType)
	'''
	v = EUDBinaryMax(lambda x:Accumulate(Player, AtLeast, x, ResourceType))
	EUDReturn(v)

@EUDCommand([argEncPlayer, argEncUnit], [retDecDecimal])
def cmd_ExKills(Player, Unit):
	'''
	Player, Unit -> Get x satisfies Kills(Player, Exactly, x, Unit)
	'''
	v = EUDBinaryMax(lambda x:Kills(Player, AtLeast, x, Unit))
	EUDReturn(v)

@EUDCommand([], [retDecDecimal])
def cmd_ExElapsedTime():
	'''
	Get x satisfies ElapsedTime(Exactly, x)
	'''
	v = EUDBinaryMax(lambda x:ElapsedTime(AtLeast, x))
	EUDReturn(v)

@EUDCommand([argEncPlayer], [retDecDecimal])
def cmd_ExOpponents(Player):
	'''
	Player -> Get x satisfies Opponents(Player, Exactly, x)
	'''
	v = EUDBinaryMax(lambda x:Opponents(Player, AtLeast, x))
	EUDReturn(v)

@EUDCommand([argEncPlayer, argEncUnit], [retDecDecimal])
def cmd_ExDeaths(Player, Unit):
	'''
	Player, Unit -> Get x satisfies Deaths(Player, Exactly, x, Unit)
	'''
	v = EUDBinaryMax(lambda x:Deaths(Player, AtLeast, x, Unit))
	EUDReturn(v)

@EUDCommand([argEncPlayer, argEncScore], [retDecDecimal])
def cmd_ExScore(Player, ScoreType):
	'''
	Player, ScoreType -> Get x satisfies Score(Player, ScoreType, Exactly, x)
	'''
	v = EUDBinaryMax(lambda x:Score(Player, ScoreType, AtLeast, x))
	EUDReturn(v)
