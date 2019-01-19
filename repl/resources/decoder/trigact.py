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
    tb_SwitchState
)
from .common import *

_actmap = EPDOffsetMap((
	('locid1', 0x00, 4),
	('strid', 0x04, 4),
	('wavid', 0x08, 4),
	('time', 0x0C, 4),
	('player1', 0x10, 4),
	('player2', 0x14, 4),
	('unitid', 0x18, 2),
	('acttype', 0x1A, 1),
	('amount', 0x1B, 1),
	('flags', 0x1C, 1),
	('internal', 0x1E, 2),
))

@EUDFunc
def dec_Action(epd):
	actions = EUDArray([
		0,
		EUDFuncPtr(1, 0)(dec_Victory),
		EUDFuncPtr(1, 0)(dec_Defeat),
		EUDFuncPtr(1, 0)(dec_PreserveTrigger),
		EUDFuncPtr(1, 0)(dec_Wait),
		EUDFuncPtr(1, 0)(dec_PauseGame),
		EUDFuncPtr(1, 0)(dec_UnpauseGame),
		EUDFuncPtr(1, 0)(dec_Transmission),
		EUDFuncPtr(1, 0)(dec_PlayWAV),
		EUDFuncPtr(1, 0)(dec_DisplayText),
		EUDFuncPtr(1, 0)(dec_CenterView),
		EUDFuncPtr(1, 0)(dec_CreateUnitWithProperties),
		EUDFuncPtr(1, 0)(dec_SetMissionObjectives),
		EUDFuncPtr(1, 0)(dec_SetSwitch),
		EUDFuncPtr(1, 0)(dec_SetCountdownTimer),
		EUDFuncPtr(1, 0)(dec_RunAIScript),
		EUDFuncPtr(1, 0)(dec_RunAIScriptAt),
		EUDFuncPtr(1, 0)(dec_LeaderBoardControl),
		EUDFuncPtr(1, 0)(dec_LeaderBoardControlAt),
		EUDFuncPtr(1, 0)(dec_LeaderBoardResources),
		EUDFuncPtr(1, 0)(dec_LeaderBoardKills),
		EUDFuncPtr(1, 0)(dec_LeaderBoardScore),
		EUDFuncPtr(1, 0)(dec_KillUnit),
		EUDFuncPtr(1, 0)(dec_KillUnitAt),
		EUDFuncPtr(1, 0)(dec_RemoveUnit),
		EUDFuncPtr(1, 0)(dec_RemoveUnitAt),
		EUDFuncPtr(1, 0)(dec_SetResources),
		EUDFuncPtr(1, 0)(dec_SetScore),
		EUDFuncPtr(1, 0)(dec_MinimapPing),
		EUDFuncPtr(1, 0)(dec_TalkingPortrait),
		EUDFuncPtr(1, 0)(dec_MuteUnitSpeech),
		EUDFuncPtr(1, 0)(dec_UnMuteUnitSpeech),
		EUDFuncPtr(1, 0)(dec_LeaderBoardComputerPlayers),
		EUDFuncPtr(1, 0)(dec_LeaderBoardGoalControl),
		EUDFuncPtr(1, 0)(dec_LeaderBoardGoalControlAt),
		EUDFuncPtr(1, 0)(dec_LeaderBoardGoalResources),
		EUDFuncPtr(1, 0)(dec_LeaderBoardGoalKills),
		EUDFuncPtr(1, 0)(dec_LeaderBoardGoalScore),
		EUDFuncPtr(1, 0)(dec_MoveLocation),
		EUDFuncPtr(1, 0)(dec_MoveUnit),
		EUDFuncPtr(1, 0)(dec_LeaderBoardGreed),
		EUDFuncPtr(1, 0)(dec_SetNextScenario),
		EUDFuncPtr(1, 0)(dec_SetDoodadState),
		EUDFuncPtr(1, 0)(dec_SetInvincibility),
		EUDFuncPtr(1, 0)(dec_CreateUnit),
		EUDFuncPtr(1, 0)(dec_SetDeaths),
		EUDFuncPtr(1, 0)(dec_Order),
		EUDFuncPtr(1, 0)(dec_Comment),
		EUDFuncPtr(1, 0)(dec_GiveUnits),
		EUDFuncPtr(1, 0)(dec_ModifyUnitHitPoints),
		EUDFuncPtr(1, 0)(dec_ModifyUnitEnergy),
		EUDFuncPtr(1, 0)(dec_ModifyUnitShields),
		EUDFuncPtr(1, 0)(dec_ModifyUnitResourceAmount),
		EUDFuncPtr(1, 0)(dec_ModifyUnitHangarCount),
		EUDFuncPtr(1, 0)(dec_PauseTimer),
		EUDFuncPtr(1, 0)(dec_UnpauseTimer),
		EUDFuncPtr(1, 0)(dec_Draw),
		EUDFuncPtr(1, 0)(dec_SetAllianceStatus),
	])
	act = _actmap(epd)
	acttype = act.acttype
	if EUDIf()([acttype >= 1, acttype < 58]):
		EUDFuncPtr(1, 0).cast(actions[acttype])(epd)
	if EUDElse()():
		_view_writer.write_f("Action(%D, %D, %D, %D, %D, %D, %D, %D, %D)",
			act.locid1,
			act.strid,
			act.wavid,
			act.time,
			act.player1,
			act.player2,
			act.unitid,
			act.acttype,
			act.amount,
		)
	EUDEndIf()
	flags = act.flags
	if EUDIf()(flags.ExactlyX(1, 1)):
		_view_writer.write_f(' WaitExecute')
	EUDEndIf()
	if EUDIf()(flags.ExactlyX(2, 2)):
		_view_writer.write_f(' IgnoreExecution')
	EUDEndIf()
	if EUDIf()(flags.ExactlyX(4, 4)):
		_view_writer.write_f(' AlwaysDisplay')
	EUDEndIf()
	_view_writer.write(0)

@EUDFunc
def dec_Victory(epd):
	_view_writer.write_f("Victory()")

@EUDFunc
def dec_Defeat(epd):
	_view_writer.write_f("Defeat()")

@EUDFunc
def dec_PreserveTrigger(epd):
	_view_writer.write_f("PreserveTrigger()")

@EUDFunc
def dec_Wait(epd):
	m = _actmap(epd)
	_view_writer.write_f("Wait(")
	_view_writer.write_decimal(m.time)
	_view_writer.write_f(")")


@EUDFunc
def dec_PauseGame(epd):
	_view_writer.write_f("PauseGame()")

@EUDFunc
def dec_UnpauseGame(epd):
	_view_writer.write_f("UnpauseGame()")

@EUDFunc
def dec_Transmission(epd):
	m = _actmap(epd)
	_view_writer.write_f("Transmission(")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeLocation(m.locid1)
	_view_writer.write_f(", ")
	writeString(m.wavid)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Modifier), m.amount)
	_view_writer.write_f(", ")
	_view_writer.write_decimal(m.time)
	_view_writer.write_f(", ")
	writeString(m.strid)
	_view_writer.write_f(")")


@EUDFunc
def dec_PlayWAV(epd):
	m = _actmap(epd)
	_view_writer.write_f("PlayWAV(")
	writeString(m.wavid)
	_view_writer.write_f(")")


@EUDFunc
def dec_DisplayText(epd):
	m = _actmap(epd)
	_view_writer.write_f("DisplayText(")
	writeString(m.strid)
	_view_writer.write_f(")")


@EUDFunc
def dec_CenterView(epd):
	m = _actmap(epd)
	_view_writer.write_f("CenterView(")
	writeLocation(m.locid1)
	_view_writer.write_f(")")


@EUDFunc
def dec_CreateUnitWithProperties(epd):
	m = _actmap(epd)
	_view_writer.write_f("CreateUnitWithProperties(")
	_view_writer.write_decimal(m.amount)
	_view_writer.write_f(", ")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeLocation(m.locid1)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Player), m.player1)
	_view_writer.write_f(", ")
	_view_writer.write_decimal(m.player2) # @TODO property
	_view_writer.write_f(")")


@EUDFunc
def dec_SetMissionObjectives(epd):
	m = _actmap(epd)
	_view_writer.write_f("SetMissionObjectives(")
	writeString(m.strid)
	_view_writer.write_f(")")


@EUDFunc
def dec_SetSwitch(epd):
	m = _actmap(epd)
	_view_writer.write_f("SetSwitch(")
	writeSwitch(m.player2)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_SwitchAction), m.amount)
	_view_writer.write_f(")")


@EUDFunc
def dec_SetCountdownTimer(epd):
	m = _actmap(epd)
	_view_writer.write_f("SetCountdownTimer(")
	writeConstant(EPD(tb_Modifier), m.amount)
	_view_writer.write_f(", ")
	_view_writer.write_decimal(m.time)
	_view_writer.write_f(")")


@EUDFunc
def dec_RunAIScript(epd):
	m = _actmap(epd)
	_view_writer.write_f("RunAIScript(")
	writeAIScript(m.player2)
	_view_writer.write_f(")")


@EUDFunc
def dec_RunAIScriptAt(epd):
	m = _actmap(epd)
	_view_writer.write_f("RunAIScriptAt(")
	writeAIScript(m.player2)
	_view_writer.write_f(", ")
	writeLocation(m.locid1)
	_view_writer.write_f(")")


@EUDFunc
def dec_LeaderBoardControl(epd):
	m = _actmap(epd)
	_view_writer.write_f("LeaderBoardControl(")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeString(m.strid)
	_view_writer.write_f(")")


@EUDFunc
def dec_LeaderBoardControlAt(epd):
	m = _actmap(epd)
	_view_writer.write_f("LeaderBoardControlAt(")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeLocation(m.locid1)
	_view_writer.write_f(", ")
	writeString(m.strid)
	_view_writer.write_f(")")


@EUDFunc
def dec_LeaderBoardResources(epd):
	m = _actmap(epd)
	_view_writer.write_f("LeaderBoardResources(")
	writeConstant(EPD(tb_Resource), m.unitid)
	_view_writer.write_f(", ")
	writeString(m.strid)
	_view_writer.write_f(")")


@EUDFunc
def dec_LeaderBoardKills(epd):
	m = _actmap(epd)
	_view_writer.write_f("LeaderBoardKills(")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeString(m.strid)
	_view_writer.write_f(")")


@EUDFunc
def dec_LeaderBoardScore(epd):
	m = _actmap(epd)
	_view_writer.write_f("LeaderBoardScore(")
	writeConstant(EPD(tb_Score), m.unitid)
	_view_writer.write_f(", ")
	writeString(m.strid)
	_view_writer.write_f(")")


@EUDFunc
def dec_KillUnit(epd):
	m = _actmap(epd)
	_view_writer.write_f("KillUnit(")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Player), m.player1)
	_view_writer.write_f(")")


@EUDFunc
def dec_KillUnitAt(epd):
	m = _actmap(epd)
	_view_writer.write_f("KillUnitAt(")
	if EUDIf()(m.amount == 0):
		_view_writer.write_f("All")
	if EUDElse()():
		_view_writer.write_decimal(m.amount)
	EUDEndIf()
	_view_writer.write_f(", ")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeLocation(m.locid1)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Player), m.player1)
	_view_writer.write_f(")")


@EUDFunc
def dec_RemoveUnit(epd):
	m = _actmap(epd)
	_view_writer.write_f("RemoveUnit(")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Player), m.player1)
	_view_writer.write_f(")")


@EUDFunc
def dec_RemoveUnitAt(epd):
	m = _actmap(epd)
	_view_writer.write_f("RemoveUnitAt(")
	if EUDIf()(m.amount == 0):
		_view_writer.write_f("All")
	if EUDElse()():
		_view_writer.write_decimal(m.amount)
	EUDEndIf()
	_view_writer.write_f(", ")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeLocation(m.locid1)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Player), m.player1)
	_view_writer.write_f(")")


@EUDFunc
def dec_SetResources(epd):
	m = _actmap(epd)
	_view_writer.write_f("SetResources(")
	writeConstant(EPD(tb_Player), m.player1)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Modifier), m.amount)
	_view_writer.write_f(", ")
	_view_writer.write_decimal(m.player2)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Resource), m.unitid)
	_view_writer.write_f(")")


@EUDFunc
def dec_SetScore(epd):
	m = _actmap(epd)
	_view_writer.write_f("SetScore(")
	writeConstant(EPD(tb_Player), m.player1)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Modifier), m.amount)
	_view_writer.write_f(", ")
	_view_writer.write_decimal(m.player2)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Score), m.unitid)
	_view_writer.write_f(")")


@EUDFunc
def dec_MinimapPing(epd):
	m = _actmap(epd)
	_view_writer.write_f("MinimapPing(")
	writeLocation(m.locid1)
	_view_writer.write_f(")")


@EUDFunc
def dec_TalkingPortrait(epd):
	m = _actmap(epd)
	_view_writer.write_f("TalkingPortrait(")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	_view_writer.write_decimal(m.time)
	_view_writer.write_f(")")


@EUDFunc
def dec_MuteUnitSpeech(epd):
	_view_writer.write_f("MuteUnitSpeech()")

@EUDFunc
def dec_UnMuteUnitSpeech(epd):
	_view_writer.write_f("UnMuteUnitSpeech()")

@EUDFunc
def dec_LeaderBoardComputerPlayers(epd):
	m = _actmap(epd)
	_view_writer.write_f("LeaderBoardComputerPlayers(")
	writeConstant(EPD(tb_PropState), m.amount)
	_view_writer.write_f(")")


@EUDFunc
def dec_LeaderBoardGoalControl(epd):
	m = _actmap(epd)
	_view_writer.write_f("LeaderBoardGoalControl(")
	_view_writer.write_decimal(m.player2)
	_view_writer.write_f(", ")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeString(m.strid)
	_view_writer.write_f(")")


@EUDFunc
def dec_LeaderBoardGoalControlAt(epd):
	m = _actmap(epd)
	_view_writer.write_f("LeaderBoardGoalControlAt(")
	_view_writer.write_decimal(m.player2)
	_view_writer.write_f(", ")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeLocation(m.locid1)
	_view_writer.write_f(", ")
	writeString(m.strid)
	_view_writer.write_f(")")


@EUDFunc
def dec_LeaderBoardGoalResources(epd):
	m = _actmap(epd)
	_view_writer.write_f("LeaderBoardGoalResources(")
	_view_writer.write_decimal(m.player2)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Resource), m.unitid)
	_view_writer.write_f(", ")
	writeString(m.strid)
	_view_writer.write_f(")")


@EUDFunc
def dec_LeaderBoardGoalKills(epd):
	m = _actmap(epd)
	_view_writer.write_f("LeaderBoardGoalKills(")
	_view_writer.write_decimal(m.player2)
	_view_writer.write_f(", ")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeString(m.strid)
	_view_writer.write_f(")")


@EUDFunc
def dec_LeaderBoardGoalScore(epd):
	m = _actmap(epd)
	_view_writer.write_f("LeaderBoardGoalScore(")
	_view_writer.write_decimal(m.player2)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Score), m.unitid)
	_view_writer.write_f(", ")
	writeString(m.strid)
	_view_writer.write_f(")")


@EUDFunc
def dec_MoveLocation(epd):
	m = _actmap(epd)
	_view_writer.write_f("MoveLocation(")
	writeLocation(m.player2)
	_view_writer.write_f(", ")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Player), m.player1)
	_view_writer.write_f(", ")
	writeLocation(m.locid1)
	_view_writer.write_f(")")


@EUDFunc
def dec_MoveUnit(epd):
	m = _actmap(epd)
	_view_writer.write_f("MoveUnit(")
	if EUDIf()(m.amount == 0):
		_view_writer.write_f("All")
	if EUDElse()():
		_view_writer.write_decimal(m.amount)
	EUDEndIf()
	_view_writer.write_f(", ")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Player), m.player1)
	_view_writer.write_f(", ")
	writeLocation(m.locid1)
	_view_writer.write_f(", ")
	writeLocation(m.player2)
	_view_writer.write_f(")")


@EUDFunc
def dec_LeaderBoardGreed(epd):
	m = _actmap(epd)
	_view_writer.write_f("LeaderBoardGreed(")
	_view_writer.write_decimal(m.player2)
	_view_writer.write_f(")")


@EUDFunc
def dec_SetNextScenario(epd):
	m = _actmap(epd)
	_view_writer.write_f("SetNextScenario(")
	writeString(m.strid)
	_view_writer.write_f(")")


@EUDFunc
def dec_SetDoodadState(epd):
	m = _actmap(epd)
	_view_writer.write_f("SetDoodadState(")
	writeConstant(EPD(tb_PropState), m.amount)
	_view_writer.write_f(", ")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Player), m.player1)
	_view_writer.write_f(", ")
	writeLocation(m.locid1)
	_view_writer.write_f(")")


@EUDFunc
def dec_SetInvincibility(epd):
	m = _actmap(epd)
	_view_writer.write_f("SetInvincibility(")
	writeConstant(EPD(tb_PropState), m.amount)
	_view_writer.write_f(", ")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Player), m.player1)
	_view_writer.write_f(", ")
	writeLocation(m.locid1)
	_view_writer.write_f(")")


@EUDFunc
def dec_CreateUnit(epd):
	m = _actmap(epd)
	_view_writer.write_f("CreateUnit(")
	_view_writer.write_decimal(m.amount)
	_view_writer.write_f(", ")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeLocation(m.locid1)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Player), m.player1)
	_view_writer.write_f(")")


@EUDFunc
def dec_SetDeaths(epd):
	m = _actmap(epd)

	# consider EUD
	if EUDIf()(EUDOr(
			[m.player1 >= 27, m.unitid < 228],
			[m.player1 < 12, m.unitid >= 228],
			[m.internal == 0x4353])):
		# check EUDX
		if EUDIf()(m.internal == 0x4353): # eudx
			_view_writer.write_f("SetMemoryX(%H, ",
				0x58A364 + 4*m.player1 + 48*m.unitid)
			writeConstant(EPD(tb_Modifier), m.amount)
			_view_writer.write_f(", %H(=%D), %H)", m.player2, m.player2, m.locid1)
		if EUDElse()():
			_view_writer.write_f("SetMemory(%H, ",
				0x58A364 + 4*m.player1 + 48*m.unitid)
			writeConstant(EPD(tb_Modifier), m.amount)
			_view_writer.write_f(", %H(=%D))", m.player2, m.player2)
		EUDEndIf()
	if EUDElse()():
		_view_writer.write_f("SetDeaths(")
		writeConstant(EPD(tb_Player), m.player1)
		_view_writer.write_f(", ")
		writeConstant(EPD(tb_Modifier), m.amount)
		_view_writer.write_f(", ")
		_view_writer.write_decimal(m.player2)
		_view_writer.write_f(", ")
		writeUnit(m.unitid)
		_view_writer.write_f(")")
	EUDEndIf()

@EUDFunc
def dec_Order(epd):
	m = _actmap(epd)
	_view_writer.write_f("Order(")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Player), m.player1)
	_view_writer.write_f(", ")
	writeLocation(m.locid1)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Order), m.amount)
	_view_writer.write_f(", ")
	writeLocation(m.player2)
	_view_writer.write_f(")")


@EUDFunc
def dec_Comment(epd):
	m = _actmap(epd)
	_view_writer.write_f("Comment(")
	writeString(m.strid)
	_view_writer.write_f(")")


@EUDFunc
def dec_GiveUnits(epd):
	m = _actmap(epd)
	_view_writer.write_f("GiveUnits(")
	if EUDIf()(m.amount == 0):
		_view_writer.write_f("All")
	if EUDElse()():
		_view_writer.write_decimal(m.amount)
	EUDEndIf()
	_view_writer.write_f(", ")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Player), m.player1)
	_view_writer.write_f(", ")
	writeLocation(m.locid1)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Player), m.player2)
	_view_writer.write_f(")")


@EUDFunc
def dec_ModifyUnitHitPoints(epd):
	m = _actmap(epd)
	_view_writer.write_f("ModifyUnitHitPoints(")
	if EUDIf()(m.amount == 0):
		_view_writer.write_f("All")
	if EUDElse()():
		_view_writer.write_decimal(m.amount)
	EUDEndIf()
	_view_writer.write_f(", ")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Player), m.player1)
	_view_writer.write_f(", ")
	writeLocation(m.locid1)
	_view_writer.write_f(", ")
	_view_writer.write_decimal(m.player2)
	_view_writer.write_f(")")


@EUDFunc
def dec_ModifyUnitEnergy(epd):
	m = _actmap(epd)
	_view_writer.write_f("ModifyUnitEnergy(")
	if EUDIf()(m.amount == 0):
		_view_writer.write_f("All")
	if EUDElse()():
		_view_writer.write_decimal(m.amount)
	EUDEndIf()
	_view_writer.write_f(", ")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Player), m.player1)
	_view_writer.write_f(", ")
	writeLocation(m.locid1)
	_view_writer.write_f(", ")
	_view_writer.write_decimal(m.player2)
	_view_writer.write_f(")")


@EUDFunc
def dec_ModifyUnitShields(epd):
	m = _actmap(epd)
	_view_writer.write_f("ModifyUnitShields(")
	if EUDIf()(m.amount == 0):
		_view_writer.write_f("All")
	if EUDElse()():
		_view_writer.write_decimal(m.amount)
	EUDEndIf()
	_view_writer.write_f(", ")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Player), m.player1)
	_view_writer.write_f(", ")
	writeLocation(m.locid1)
	_view_writer.write_f(", ")
	_view_writer.write_decimal(m.player2)
	_view_writer.write_f(")")


@EUDFunc
def dec_ModifyUnitResourceAmount(epd):
	m = _actmap(epd)
	_view_writer.write_f("ModifyUnitResourceAmount(")
	if EUDIf()(m.amount == 0):
		_view_writer.write_f("All")
	if EUDElse()():
		_view_writer.write_decimal(m.amount)
	EUDEndIf()
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Player), m.player1)
	_view_writer.write_f(", ")
	writeLocation(m.locid1)
	_view_writer.write_f(", ")
	_view_writer.write_decimal(m.player2)
	_view_writer.write_f(")")


@EUDFunc
def dec_ModifyUnitHangarCount(epd):
	m = _actmap(epd)
	_view_writer.write_f("ModifyUnitHangarCount(")
	_view_writer.write_decimal(m.player2)
	_view_writer.write_f(", ")
	if EUDIf()(m.amount == 0):
		_view_writer.write_f("All")
	if EUDElse()():
		_view_writer.write_decimal(m.amount)
	EUDEndIf()
	_view_writer.write_f(", ")
	writeUnit(m.unitid)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_Player), m.player1)
	_view_writer.write_f(", ")
	writeLocation(m.locid1)
	_view_writer.write_f(")")


@EUDFunc
def dec_PauseTimer(epd):
	_view_writer.write_f("PauseTimer()")

@EUDFunc
def dec_UnpauseTimer(epd):
	_view_writer.write_f("UnpauseTimer()")

@EUDFunc
def dec_Draw(epd):
	_view_writer.write_f("Draw()")

@EUDFunc
def dec_SetAllianceStatus(epd):
	m = _actmap(epd)
	_view_writer.write_f("SetAllianceStatus(")
	writeConstant(EPD(tb_Player), m.player1)
	_view_writer.write_f(", ")
	writeConstant(EPD(tb_AllyStatus), m.unitid)
	_view_writer.write_f(")")

