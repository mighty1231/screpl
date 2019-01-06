from eudplib import *

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

def testSelfMod():
	a = NextTrigger()
	nxt = Forward()

	RawTrigger(
		actions = [
			CreateUnit(1, 0, "Anywhere", P1),
			SetNextPtr(a, nxt)
		]
	)

	DoActions(CreateUnit(1, "Terran Ghost", "Anywhere", P1)) # Not activated!

	nxt << RawTrigger(
			actions = CreateUnit(1, "Terran SCV", "Anywhere", P1)
		)
@EUDFunc
def bpmain():
	from repl import (REPL, EUDByteRW, EUDCommand,
		argEncNumber, RegisterCommand, makeEPDText)
	if EUDInfLoop()():
		# Turbo
		# DoActions(SetDeaths(203151, SetTo, 1, 0))

		bpON = EUDVariable(1)

		nxt = Forward()
		DoActions(CreateUnit(1, 'Terran Marine', 'Anywhere', P1))
		if EUDInfLoop()():
			REPL().execute()
			DoActions(CreateUnit(1, 'Terran SCV', 'Anywhere', P1))
			f_simpleprint(bpON)
			EUDJumpIf(bpON == 0, nxt)
			EUDDoEvents()
			DoActions(CreateUnit(1, 'Terran Ghost', 'Anywhere', P1))
		EUDEndInfLoop()
		nxt << NextTrigger()
		DoActions(CreateUnit(1, 'Terran Firebat', 'Anywhere', P1))

		RunTrigTrigger()
		EUDDoEvents()
	EUDEndInfLoop()

	@EUDCommand([])
	def toggleBP():
		f_simpleprint('hello', bpON)
		DoActions(SetMemoryX(bpON.getValueAddr(), Add, 1, 1))
	RegisterCommand('abc', toggleBP)

def findCommentedTrigger(breakpoints):
	from repl import f_strcmp_ptrepd, makeEPDText
	# Find trigger with action Comment("screpl_bp")
	'''
	Action class.

	Memory layout.

	 ======  ============= ========  ==========
	 Offset  Field Name    Position  EPD Player
	 ======  ============= ========  ==========
	   +00   locid1         dword0   EPD(act)+0
	   +04   strid          dword1   EPD(act)+1
	   +08   wavid          dword2   EPD(act)+2
	   +0C   time           dword3   EPD(act)+3
	   +10   player1        dword4   EPD(act)+4
	   +14   player2        dword5   EPD(act)+5
	   +18   unitid         dword6   EPD(act)+6
	   +1A   acttype
	   +1B   amount
	   +1C   flags          dword7   EPD(act)+7
	   +1D   internal[3
	 ======  ============= ========  ==========
	'''

	actmap = EPDOffsetMap((
		('locid1', 0x00, 4),
		('strid', 0x04, 4),
		('wavid', 0x08, 4),
		('time', 0x0C, 4),
		('player1', 0x10, 4),
		('player2', 0x14, 4),
		('unitid', 0x18, 2),
		('acttype', 0x1A, 1),
		('amount', 0x1B, 1),
		('flags', 0x1C, 2),
		('eudx', 0x1E, 2),
	))

	# for i in range(8):
	# 	f_simpleprint(hptr(TrigTriggerBegin(i)), hptr(TrigTriggerEnd(i)))
	for pid in range(8):
		# Loop over map trigger
		getNxtTrigger = Forward()

		trig_ptr = TrigTriggerBegin(pid)
		trig_epd = EPD(trig_ptr)

		trigend_ptr = TrigTriggerEnd(pid)

		if EUDInfLoop()():
			EUDBreakIf(trig_ptr == trigend_ptr)
			EUDBreakIf(trig_ptr == 0)

			# search act
			act_epd = EUDVariable()
			act_epd << trig_epd + (8 + 16*20)//4
			if EUDLoopN()(64):
				m = actmap(act_epd)

				# Check it is comment trigger
				if EUDIf()([m.acttype == 47]):
					# search string
					straddr = GetMapStringAddr(m.strid)
					if EUDIf()(f_strcmp_ptrepd(straddr, makeEPDText("screpl_bp")) == 0):
						breakpoints.push(trig_ptr)
						EUDJump(getNxtTrigger)
					EUDEndIf()

				EUDEndIf()

				act_epd += 32 // 4
			EUDEndLoopN()

			getNxtTrigger << NextTrigger()

			# next trigger
			p, e = f_dwepdread_epd(trig_epd + 1)
			trig_ptr << p
			trig_epd << e
		EUDEndInfLoop()


@EUDTypedFunc([None, EUDFuncPtr(2, 0)])
def installHook_epd(prev_trigptr, hook):
	prev_trigepd = EPD(prev_trigptr)
	f_simpleprint(hptr(prev_trigptr), prev_trigepd)
	trig_ptr, trig_epd = f_dwepdread_epd(prev_trigepd + 1)

	# function scope
	if PushTriggerScope():
		_start = NextTrigger()

		# Recover original trigger loop
		f_dwwrite_epd(prev_trigepd + 1, trig_ptr)

		f_simpleprint("??")
		# function hook
		hook(trig_ptr, trig_epd)

		_end = RawTrigger()
	PopTriggerScope()

	# patch hook
	f_simpleprint("Patching...")
	DoActions([
		SetNextPtr(prev_trigptr, _start),
		SetNextPtr(_end, trig_ptr)
	])


@EUDFunc
def test(a, b):
	f_simpleprint('in hook', hptr(a), b)

@EUDFunc
def main():
	from repl import REPL, EUDCommand, StaticView, RegisterCommand, makeEPDText, EUDByteRW
	if EUDExecuteOnce()():
		breakpoints = EUDStack()(30)
		findCommentedTrigger(breakpoints)
		f_simpleprint(breakpoints.pos, breakpoints.data[0])
		installHook_epd(breakpoints.data[0], test)
	EUDEndExecuteOnce()
	@EUDCommand([])
	def cmd_openBPView():
		arr = EUDArray([
			makeEPDText("Breakpoints"),
			30,
		] + [EPD(Db(30)) for _ in range(30)])
		i = EUDVariable()
		i << 0
		data = breakpoints.data
		if EUDWhile()(i < 1):
			writer = EUDByteRW()
			writer.seekepd(arr[i+2])
			writer.write_strepd(makeEPDText("bp "))
			writer.write_hex(data[i])
			writer.write(0)
			i += 1
		EUDEndWhile()
		StaticView.OpenView(EPD(arr))
	RegisterCommand("bp", cmd_openBPView)

	if EUDInfLoop()():
		DoActions(SetDeaths(203151, SetTo, 1, 0))
		# REPL().execute()
		RunTrigTrigger()
		EUDDoEvents()
	EUDEndInfLoop()

@EUDFunc
def bptest_main():
	from repl import REPL, RegisterBPHere
	if EUDInfLoop()():
		# Turbo
		DoActions(SetDeaths(203151, SetTo, 1, 0))
		REPL().execute()

		DoActions(CreateUnit(1, "Terran Battlecruiser", "Anywhere", P1))
		RegisterBPHere("Here!")
		DoActions(KillUnit("Terran Battlecruiser", P1))

		RunTrigTrigger()
		EUDDoEvents()
	EUDEndInfLoop()

from config import outfname
LoadMap("base.scx")
SaveMap(outfname, bptest_main)

