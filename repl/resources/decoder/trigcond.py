from eudplib import *
from ...view.view import _view_writer
from ..table.tables import (
    tb_Modifier,
    tb_AllyStatus,
    tb_Comparison,
    tb_Order,
    tb_Player,
    tb_PropState,
    tb_Resource,
    tb_Score,
    tb_SwitchAction,
    tb_SwitchState,
)
from .common import *

_condmap = EPDOffsetMap((
	('locid', 0x00, 4),
	('player', 0x04, 4),
	('amount', 0x08, 4),
	('unitid', 0x0C, 2),
	('comparison', 0x0E, 1),
	('condtype', 0x0F, 1),
	('restype', 0x10, 1),
	('flags', 0x11, 1),
	('internal', 0x12, 2),
))

@EUDFunc
def dec_Condition(epd):
	conditions = EUDArray([
		0,
		EUDFuncPtr(1, 0)(dec_CountdownTimer),
		EUDFuncPtr(1, 0)(dec_Command),
		EUDFuncPtr(1, 0)(dec_Bring),
		EUDFuncPtr(1, 0)(dec_Accumulate),
		EUDFuncPtr(1, 0)(dec_Kills),
		EUDFuncPtr(1, 0)(dec_CommandMost),
		EUDFuncPtr(1, 0)(dec_CommandMostAt),
		EUDFuncPtr(1, 0)(dec_MostKills),
		EUDFuncPtr(1, 0)(dec_HighestScore),
		EUDFuncPtr(1, 0)(dec_MostResources),
		EUDFuncPtr(1, 0)(dec_Switch),
		EUDFuncPtr(1, 0)(dec_ElapsedTime),
		EUDFuncPtr(1, 0)(dec_Always), # Actually this should be Briefing()
		EUDFuncPtr(1, 0)(dec_Opponents),
		EUDFuncPtr(1, 0)(dec_Deaths),
		EUDFuncPtr(1, 0)(dec_CommandLeast),
		EUDFuncPtr(1, 0)(dec_CommandLeastAt),
		EUDFuncPtr(1, 0)(dec_LeastKills),
		EUDFuncPtr(1, 0)(dec_LowestScore),
		EUDFuncPtr(1, 0)(dec_LeastResources),
		EUDFuncPtr(1, 0)(dec_Score),
		EUDFuncPtr(1, 0)(dec_Always),
		EUDFuncPtr(1, 0)(dec_Never),
	])
	cond = _condmap(epd)
	condtype = cond.condtype
	if EUDIf()([condtype >= 1, condtype < 24]):
		EUDFuncPtr(1, 0).cast(conditions[condtype])(epd)
	if EUDElse()():
		_view_writer.write_f("Condition(%D, %D, %D, %D, %D, %D, %D, %D, %D)",
			cond.locid,
			cond.player,
			cond.amount,
			cond.unitid,
			cond.comparison,
			cond.condtype,
			cond.restype,
			cond.flags,
			cond.internal,
		)
	EUDEndIf()
	_view_writer.write(0)

@EUDFunc
def dec_CountdownTimer(epd):
	m = _condmap(epd)
	_view_writer.write_f("CountdownTimer(")
	writeConstant(EPD(tb_Comparison), m.comparison)
	_view_writer.write_f(", ")
	_view_writer.write_decimal(m.amount)
	_view_writer.write_f(")")


@EUDFunc
def dec_Command(epd):
	m = _condmap(epd)
	_view_writer.write_f("Command(")
	writeConstant(EPD(tb_Player), m.player)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Comparison), m.comparison)
	_view_writer.write_f(", ")
	_view_writer.write_decimal(m.amount)
	_view_writer.write_f(", ")
	writeUnit(m.unitid)
	_view_writer.write_f(")")


@EUDFunc
def dec_Bring(epd):
	m = _condmap(epd)
	_view_writer.write_f("Bring(")
	writeConstant(EPD(tb_Player), m.player)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Comparison), m.comparison)
	_view_writer.write_f(", ")
	_view_writer.write_decimal(m.amount)
	_view_writer.write_f(", ")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeLocation(m.locid)
	_view_writer.write_f(")")


@EUDFunc
def dec_Accumulate(epd):
	m = _condmap(epd)
	_view_writer.write_f("Accumulate(")
	writeConstant(EPD(tb_Player), m.player)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Comparison), m.comparison)
	_view_writer.write_f(", ")
	_view_writer.write_decimal(m.amount)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Resource), m.restype)
	_view_writer.write_f(")")


@EUDFunc
def dec_Kills(epd):
	m = _condmap(epd)
	_view_writer.write_f("Kills(")
	writeConstant(EPD(tb_Player), m.player)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Comparison), m.comparison)
	_view_writer.write_f(", ")
	_view_writer.write_decimal(m.amount)
	_view_writer.write_f(", ")
	writeUnit(m.unitid)
	_view_writer.write_f(")")


@EUDFunc
def dec_CommandMost(epd):
	m = _condmap(epd)
	_view_writer.write_f("CommandMost(")
	writeUnit(m.unitid)
	_view_writer.write_f(")")


@EUDFunc
def dec_CommandMostAt(epd):
	m = _condmap(epd)
	_view_writer.write_f("CommandMostAt(")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeLocation(m.locid)
	_view_writer.write_f(")")


@EUDFunc
def dec_MostKills(epd):
	m = _condmap(epd)
	_view_writer.write_f("MostKills(")
	writeUnit(m.unitid)
	_view_writer.write_f(")")


@EUDFunc
def dec_HighestScore(epd):
	m = _condmap(epd)
	_view_writer.write_f("HighestScore(")
	writeConstant(EPD(tb_Score), m.restype)
	_view_writer.write_f(")")


@EUDFunc
def dec_MostResources(epd):
	m = _condmap(epd)
	_view_writer.write_f("MostResources(")
	writeConstant(EPD(tb_Resource), m.restype)
	_view_writer.write_f(")")


@EUDFunc
def dec_Switch(epd):
	m = _condmap(epd)
	_view_writer.write_f("Switch(")
	writeSwitch(m.restype)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_SwitchState), m.comparison)
	_view_writer.write_f(")")


@EUDFunc
def dec_ElapsedTime(epd):
	m = _condmap(epd)
	_view_writer.write_f("ElapsedTime(")
	writeConstant(EPD(tb_Comparison), m.comparison)
	_view_writer.write_f(", ")
	_view_writer.write_decimal(m.amount)
	_view_writer.write_f(")")


@EUDFunc
def dec_Opponents(epd):
	m = _condmap(epd)
	_view_writer.write_f("Opponents(")
	writeConstant(EPD(tb_Player), m.player)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Comparison), m.comparison)
	_view_writer.write_f(", ")
	_view_writer.write_decimal(m.amount)
	_view_writer.write_f(")")


@EUDFunc
def dec_Deaths(epd):
	m = _condmap(epd)

	# consider EUD
	if EUDIf()(EUDOr(
			[m.player >= 27, m.unitid < 228],
			[m.player < 12, m.unitid >= 228],
			[m.internal == 0x4353])):
		# check EUDX
		if EUDIf()(m.internal == 0x4353): # eudx
			_view_writer.write_f("MemoryX(%H, ",
				0x58A364 + 4*m.player + 48*m.unitid)
			writeConstant(EPD(tb_Comparison), m.comparison)
			_view_writer.write_f(", %H(=%D), %H)", m.amount, m.amount, m.locid)
		if EUDElse()():
			_view_writer.write_f("Memory(%H, ",
				0x58A364 + 4*m.player + 48*m.unitid)
			writeConstant(EPD(tb_Comparison), m.comparison)
			_view_writer.write_f(", %H(=%D))", m.amount, m.amount)
		EUDEndIf()
	if EUDElse()():
		_view_writer.write_f("Deaths(")
		writeConstant(EPD(tb_Player), m.player)
		_view_writer.write_f(", ")
		writeConstant(EPD(tb_Comparison), m.comparison)
		_view_writer.write_f(", ")
		_view_writer.write_decimal(m.amount)
		_view_writer.write_f(", ")
		writeUnit(m.unitid)
		_view_writer.write_f(")")
	EUDEndIf()


@EUDFunc
def dec_CommandLeast(epd):
	m = _condmap(epd)
	_view_writer.write_f("CommandLeast(")
	writeUnit(m.unitid)
	_view_writer.write_f(")")


@EUDFunc
def dec_CommandLeastAt(epd):
	m = _condmap(epd)
	_view_writer.write_f("CommandLeastAt(")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeLocation(m.locid)
	_view_writer.write_f(")")


@EUDFunc
def dec_LeastKills(epd):
	m = _condmap(epd)
	_view_writer.write_f("LeastKills(")
	writeUnit(m.unitid)
	_view_writer.write_f(")")


@EUDFunc
def dec_LowestScore(epd):
	m = _condmap(epd)
	_view_writer.write_f("LowestScore(")
	writeConstant(EPD(tb_Score), m.restype)
	_view_writer.write_f(")")


@EUDFunc
def dec_LeastResources(epd):
	m = _condmap(epd)
	_view_writer.write_f("LeastResources(")
	writeConstant(EPD(tb_Resource), m.restype)
	_view_writer.write_f(")")


@EUDFunc
def dec_Score(epd):
	m = _condmap(epd)
	_view_writer.write_f("Score(")
	writeConstant(EPD(tb_Player), m.player)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Score), m.restype)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Comparison), m.comparison)
	_view_writer.write_f(", ")
	_view_writer.write_decimal(m.amount)
	_view_writer.write_f(")")


@EUDFunc
def dec_Always(epd):
	_view_writer.write_f("Always()")

@EUDFunc
def dec_Never(epd):
	_view_writer.write_f("Never()")
