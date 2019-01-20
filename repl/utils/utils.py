from eudplib import *
from .eudbyterw import EUDByteRW

_byterw1 = EUDByteRW()
_byterw2 = EUDByteRW()

def f_raiseError(txt):
	DoActions([
		SetCurrentPlayer(f_getuserplayerid()),
		DisplayText(txt),
		SetMemory(0, Add, 1),
	])

def f_raiseWarning(txt):
	DoActions([
		SetCurrentPlayer(f_getuserplayerid()),
		DisplayText(txt),
	])

@EUDFunc
def f_print_utf8_epd(epd):
	sp = EUDVariable(0)
	strId = EncodeString("_" * 2048)
	if EUDExecuteOnce()():
		sp << GetMapStringAddr(strId)
	EUDEndExecuteOnce()

	_byterw1.seekoffset(sp)
	_byterw1.write_strepd(epd)
	_byterw1.write(0)
	DoActions(DisplayText(strId))

@EUDFunc
def f_print_memorytable(off):
	f_simpleprint('Memory table offset = ', hptr(off))
	a = DBString(100)
	_byterw1.seekoffset(a.GetStringMemoryAddr())
	_byterw1.write_strepd(EPDConstString('- '))
	_byterw1.write_memoryTable(off, 8)
	_byterw1.write_strn(off, 8)
	_byterw1.write(0)
	a.Display()

@EUDFunc
def f_epd2ptr(epd):
	EUDReturn(0x58A364 + epd * 4)

@EUDFunc
def f_print_memorytable_epd(epd):
	off = f_epd2ptr(epd)
	f_simpleprint('Memory table offset epd = ', hptr(off))
	a = DBString(100)
	_byterw1.seekoffset(a.GetStringMemoryAddr())
	_byterw1.write_strepd(EPDConstString('- '))
	_byterw1.write_memoryTable(off, 8)
	_byterw1.write_strn(off, 8)
	_byterw1.write(0)
	a.Display()

@EUDFunc
def f_strcpy2(dest, src):
	''' s1, s2: ptr '''
	_byterw1.seekoffset(dest)
	_byterw1.write_str(src)

@EUDFunc
def f_strcmp2(s1, s2):
	''' s1, s2: ptr '''
	_byterw1.seekoffset(s1)
	_byterw2.seekoffset(s2)

	if EUDInfLoop()():
		ch1 = _byterw1.read()
		ch2 = _byterw2.read()
		if EUDIf()(ch1 == ch2):
			if EUDIf()(ch1 == 0):
				EUDReturn(0)
			EUDEndIf()
			EUDContinue()
		if EUDElse()():
			EUDReturn(ch1 - ch2)
		EUDEndIf()
	EUDEndInfLoop()

@EUDFunc
def f_strcmp_epd(s1, s2):
	''' s1, s2: epd '''
	_byterw1.seekepd(s1)
	_byterw2.seekepd(s2)

	if EUDInfLoop()():
		ch1 = _byterw1.read()
		ch2 = _byterw2.read()
		if EUDIf()(ch1 == ch2):
			if EUDIf()(ch1 == 0):
				EUDReturn(0)
			EUDEndIf()
			EUDContinue()
		if EUDElse()():
			EUDReturn(ch1 - ch2)
		EUDEndIf()
	EUDEndInfLoop()

@EUDFunc
def f_strcmp_ptrepd(s1, s2):
	''' s1: ptr, s2: epd '''
	_byterw1.seekoffset(s1)
	_byterw2.seekepd(s2)

	if EUDInfLoop()():
		ch1 = _byterw1.read()
		ch2 = _byterw2.read()
		if EUDIf()(ch1 == ch2):
			if EUDIf()(ch1 == 0):
				EUDReturn(0)
			EUDEndIf()
			EUDContinue()
		if EUDElse()():
			EUDReturn(ch1 - ch2)
		EUDEndIf()
	EUDEndInfLoop()

@EUDFunc
def f_strlen(s):
	_byterw1 = EUDByteRW()
	cnt = EUDVariable()

	_byterw1.seekoffset(s)
	cnt << 0
	if EUDInfLoop()():
		ch = _byterw1.read()
		EUDBreakIf(ch == 0)
		DoActions(cnt.AddNumber(1))
	EUDEndInfLoop()
	EUDReturn(cnt)

@EUDFunc
def f_memcmp(p1, p2, cnt):
	''' p1, p2: ptr '''
	_byterw1.seekoffset(p1)
	_byterw2.seekoffset(p2)

	if EUDInfLoop()():
		EUDBreakIf(cnt == 0)
		ch1 = _byterw1.read()
		ch2 = _byterw2.read()
		if EUDIf()(ch1 == ch2):
			cnt -= 1
			EUDContinue()
		EUDEndIf()
		EUDReturn(ch1 - ch2)
	EUDEndInfLoop()
	EUDReturn(0)
