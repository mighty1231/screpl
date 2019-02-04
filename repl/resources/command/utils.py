from eudplib import *
from ...utils import EPDConstString, EUDByteRW
from ...core.command import EUDCommand, registerCommand
from ...core.decoder import retDecDecimal, retDecHex, retDecBinary
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
from ...view import StaticView

def register_utilcmds():
	# EUDVariable
	registerCommand('mul', cmd_mul)
	registerCommand('div', cmd_div)

	# Memory manipulation
	registerCommand('dwread', cmd_dwread)
	registerCommand('wread', cmd_wread)
	registerCommand('bread', cmd_bread)
	registerCommand('dwwrite', cmd_dwwrite)
	registerCommand('wwrite', cmd_wwrite)
	registerCommand('bwrite', cmd_bwrite)
	registerCommand('memcpy', cmd_memcpy)
	registerCommand('strcpy', cmd_strcpy)

	# Memory view
	registerCommand('mv', cmd_memoryview)

	# Extended Conditions
	registerCommand('exCountdownTimer', cmd_ExCountdownTimer)
	registerCommand('exCommand', cmd_ExCommand)
	registerCommand('exBring', cmd_ExBring)
	registerCommand('exAccumulate', cmd_ExAccumulate)
	registerCommand('exKills', cmd_ExKills)
	registerCommand('exElapsedTime', cmd_ExElapsedTime)
	registerCommand('exOpponents', cmd_ExOpponents)
	registerCommand('exDeaths', cmd_ExDeaths)
	registerCommand('exScore', cmd_ExScore)

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
