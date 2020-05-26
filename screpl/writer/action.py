from eudplib import *
from screpl.resources.table import tables as tb
from . import (
    get_main_writer,
    write_aiscript,
    write_constant,
    write_location,
    write_switch,
    write_string,
    write_unit,
)

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
def write_action_epd(epd):
    actions = EUDArray([
        0,
        EUDFuncPtr(1, 0)(_writeVictory),
        EUDFuncPtr(1, 0)(_writeDefeat),
        EUDFuncPtr(1, 0)(_writePreserveTrigger),
        EUDFuncPtr(1, 0)(_writeWait),
        EUDFuncPtr(1, 0)(_writePauseGame),
        EUDFuncPtr(1, 0)(_writeUnpauseGame),
        EUDFuncPtr(1, 0)(_writeTransmission),
        EUDFuncPtr(1, 0)(_writePlayWAV),
        EUDFuncPtr(1, 0)(_writeDisplayText),
        EUDFuncPtr(1, 0)(_writeCenterView),
        EUDFuncPtr(1, 0)(_writeCreateUnitWithProperties),
        EUDFuncPtr(1, 0)(_writeSetMissionObjectives),
        EUDFuncPtr(1, 0)(_writeSetSwitch),
        EUDFuncPtr(1, 0)(_writeSetCountdownTimer),
        EUDFuncPtr(1, 0)(_writeRunAIScript),
        EUDFuncPtr(1, 0)(_writeRunAIScriptAt),
        EUDFuncPtr(1, 0)(_writeLeaderBoardControl),
        EUDFuncPtr(1, 0)(_writeLeaderBoardControlAt),
        EUDFuncPtr(1, 0)(_writeLeaderBoardResources),
        EUDFuncPtr(1, 0)(_writeLeaderBoardKills),
        EUDFuncPtr(1, 0)(_writeLeaderBoardScore),
        EUDFuncPtr(1, 0)(_writeKillUnit),
        EUDFuncPtr(1, 0)(_writeKillUnitAt),
        EUDFuncPtr(1, 0)(_writeRemoveUnit),
        EUDFuncPtr(1, 0)(_writeRemoveUnitAt),
        EUDFuncPtr(1, 0)(_writeSetResources),
        EUDFuncPtr(1, 0)(_writeSetScore),
        EUDFuncPtr(1, 0)(_writeMinimapPing),
        EUDFuncPtr(1, 0)(_writeTalkingPortrait),
        EUDFuncPtr(1, 0)(_writeMuteUnitSpeech),
        EUDFuncPtr(1, 0)(_writeUnMuteUnitSpeech),
        EUDFuncPtr(1, 0)(_writeLeaderBoardComputerPlayers),
        EUDFuncPtr(1, 0)(_writeLeaderBoardGoalControl),
        EUDFuncPtr(1, 0)(_writeLeaderBoardGoalControlAt),
        EUDFuncPtr(1, 0)(_writeLeaderBoardGoalResources),
        EUDFuncPtr(1, 0)(_writeLeaderBoardGoalKills),
        EUDFuncPtr(1, 0)(_writeLeaderBoardGoalScore),
        EUDFuncPtr(1, 0)(_writeMoveLocation),
        EUDFuncPtr(1, 0)(_writeMoveUnit),
        EUDFuncPtr(1, 0)(_writeLeaderBoardGreed),
        EUDFuncPtr(1, 0)(_writeSetNextScenario),
        EUDFuncPtr(1, 0)(_writeSetDoodadState),
        EUDFuncPtr(1, 0)(_writeSetInvincibility),
        EUDFuncPtr(1, 0)(_writeCreateUnit),
        EUDFuncPtr(1, 0)(_writeSetDeaths),
        EUDFuncPtr(1, 0)(_writeOrder),
        EUDFuncPtr(1, 0)(_writeComment),
        EUDFuncPtr(1, 0)(_writeGiveUnits),
        EUDFuncPtr(1, 0)(_writeModifyUnitHitPoints),
        EUDFuncPtr(1, 0)(_writeModifyUnitEnergy),
        EUDFuncPtr(1, 0)(_writeModifyUnitShields),
        EUDFuncPtr(1, 0)(_writeModifyUnitResourceAmount),
        EUDFuncPtr(1, 0)(_writeModifyUnitHangarCount),
        EUDFuncPtr(1, 0)(_writePauseTimer),
        EUDFuncPtr(1, 0)(_writeUnpauseTimer),
        EUDFuncPtr(1, 0)(_writeDraw),
        EUDFuncPtr(1, 0)(_writeSetAllianceStatus),
    ])
    act = _actmap(epd)
    acttype = act.acttype
    if EUDIf()([acttype >= 1, acttype < 58]):
        EUDFuncPtr(1, 0).cast(actions[acttype])(epd)
    if EUDElse()():
        get_main_writer().write_f(
            "Action(%D, %D, %D, %D, %D, %D, %D, %D, %D)",
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
        get_main_writer().write_f(' WaitExecute')
    EUDEndIf()
    if EUDIf()(flags.ExactlyX(2, 2)):
        get_main_writer().write_f(' IgnoreExecution')
    EUDEndIf()
    if EUDIf()(flags.ExactlyX(4, 4)):
        get_main_writer().write_f(' AlwaysDisplay')
    EUDEndIf()

@EUDFunc
def _writeVictory(epd):
    get_main_writer().write_f("Victory()")

@EUDFunc
def _writeDefeat(epd):
    get_main_writer().write_f("Defeat()")

@EUDFunc
def _writePreserveTrigger(epd):
    get_main_writer().write_f("PreserveTrigger()")

@EUDFunc
def _writeWait(epd):
    m = _actmap(epd)
    get_main_writer().write_f("Wait(")
    get_main_writer().write_decimal(m.time)
    get_main_writer().write_f(")")


@EUDFunc
def _writePauseGame(epd):
    get_main_writer().write_f("PauseGame()")

@EUDFunc
def _writeUnpauseGame(epd):
    get_main_writer().write_f("UnpauseGame()")

@EUDFunc
def _writeTransmission(epd):
    m = _actmap(epd)
    get_main_writer().write_f("Transmission(")
    write_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_location(m.locid1)
    get_main_writer().write_f(", ")
    write_string(m.wavid)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Modifier), m.amount)
    get_main_writer().write_f(", ")
    get_main_writer().write_decimal(m.time)
    get_main_writer().write_f(", ")
    write_string(m.strid)
    get_main_writer().write_f(")")


@EUDFunc
def _writePlayWAV(epd):
    m = _actmap(epd)
    get_main_writer().write_f("PlayWAV(")
    write_string(m.wavid)
    get_main_writer().write_f(")")


@EUDFunc
def _writeDisplayText(epd):
    m = _actmap(epd)
    get_main_writer().write_f("DisplayText(")
    write_string(m.strid)
    get_main_writer().write_f(")")


@EUDFunc
def _writeCenterView(epd):
    m = _actmap(epd)
    get_main_writer().write_f("CenterView(")
    write_location(m.locid1)
    get_main_writer().write_f(")")


@EUDFunc
def _writeCreateUnitWithProperties(epd):
    m = _actmap(epd)
    get_main_writer().write_f("CreateUnitWithProperties(")
    get_main_writer().write_decimal(m.amount)
    get_main_writer().write_f(", ")
    write_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_location(m.locid1)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Player), m.player1)
    get_main_writer().write_f(", ")
    get_main_writer().write_decimal(m.player2) # @TODO property
    get_main_writer().write_f(")")


@EUDFunc
def _writeSetMissionObjectives(epd):
    m = _actmap(epd)
    get_main_writer().write_f("SetMissionObjectives(")
    write_string(m.strid)
    get_main_writer().write_f(")")


@EUDFunc
def _writeSetSwitch(epd):
    m = _actmap(epd)
    get_main_writer().write_f("SetSwitch(")
    write_switch(m.player2)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.SwitchAction), m.amount)
    get_main_writer().write_f(")")


@EUDFunc
def _writeSetCountdownTimer(epd):
    m = _actmap(epd)
    get_main_writer().write_f("SetCountdownTimer(")
    write_constant(EPD(tb.Modifier), m.amount)
    get_main_writer().write_f(", ")
    get_main_writer().write_decimal(m.time)
    get_main_writer().write_f(")")


@EUDFunc
def _writeRunAIScript(epd):
    m = _actmap(epd)
    get_main_writer().write_f("RunAIScript(")
    write_aiscript(m.player2)
    get_main_writer().write_f(")")


@EUDFunc
def _writeRunAIScriptAt(epd):
    m = _actmap(epd)
    get_main_writer().write_f("RunAIScriptAt(")
    write_aiscript(m.player2)
    get_main_writer().write_f(", ")
    write_location(m.locid1)
    get_main_writer().write_f(")")


@EUDFunc
def _writeLeaderBoardControl(epd):
    m = _actmap(epd)
    get_main_writer().write_f("LeaderBoardControl(")
    write_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_string(m.strid)
    get_main_writer().write_f(")")


@EUDFunc
def _writeLeaderBoardControlAt(epd):
    m = _actmap(epd)
    get_main_writer().write_f("LeaderBoardControlAt(")
    write_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_location(m.locid1)
    get_main_writer().write_f(", ")
    write_string(m.strid)
    get_main_writer().write_f(")")


@EUDFunc
def _writeLeaderBoardResources(epd):
    m = _actmap(epd)
    get_main_writer().write_f("LeaderBoardResources(")
    write_constant(EPD(tb.Resource), m.unitid)
    get_main_writer().write_f(", ")
    write_string(m.strid)
    get_main_writer().write_f(")")


@EUDFunc
def _writeLeaderBoardKills(epd):
    m = _actmap(epd)
    get_main_writer().write_f("LeaderBoardKills(")
    write_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_string(m.strid)
    get_main_writer().write_f(")")


@EUDFunc
def _writeLeaderBoardScore(epd):
    m = _actmap(epd)
    get_main_writer().write_f("LeaderBoardScore(")
    write_constant(EPD(tb.Score), m.unitid)
    get_main_writer().write_f(", ")
    write_string(m.strid)
    get_main_writer().write_f(")")


@EUDFunc
def _writeKillUnit(epd):
    m = _actmap(epd)
    get_main_writer().write_f("KillUnit(")
    write_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Player), m.player1)
    get_main_writer().write_f(")")


@EUDFunc
def _writeKillUnitAt(epd):
    m = _actmap(epd)
    get_main_writer().write_f("KillUnitAt(")
    if EUDIf()(m.amount == 0):
        get_main_writer().write_f("All")
    if EUDElse()():
        get_main_writer().write_decimal(m.amount)
    EUDEndIf()
    get_main_writer().write_f(", ")
    write_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_location(m.locid1)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Player), m.player1)
    get_main_writer().write_f(")")


@EUDFunc
def _writeRemoveUnit(epd):
    m = _actmap(epd)
    get_main_writer().write_f("RemoveUnit(")
    write_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Player), m.player1)
    get_main_writer().write_f(")")


@EUDFunc
def _writeRemoveUnitAt(epd):
    m = _actmap(epd)
    get_main_writer().write_f("RemoveUnitAt(")
    if EUDIf()(m.amount == 0):
        get_main_writer().write_f("All")
    if EUDElse()():
        get_main_writer().write_decimal(m.amount)
    EUDEndIf()
    get_main_writer().write_f(", ")
    write_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_location(m.locid1)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Player), m.player1)
    get_main_writer().write_f(")")


@EUDFunc
def _writeSetResources(epd):
    m = _actmap(epd)
    get_main_writer().write_f("SetResources(")
    write_constant(EPD(tb.Player), m.player1)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Modifier), m.amount)
    get_main_writer().write_f(", ")
    get_main_writer().write_decimal(m.player2)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Resource), m.unitid)
    get_main_writer().write_f(")")


@EUDFunc
def _writeSetScore(epd):
    m = _actmap(epd)
    get_main_writer().write_f("SetScore(")
    write_constant(EPD(tb.Player), m.player1)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Modifier), m.amount)
    get_main_writer().write_f(", ")
    get_main_writer().write_decimal(m.player2)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Score), m.unitid)
    get_main_writer().write_f(")")


@EUDFunc
def _writeMinimapPing(epd):
    m = _actmap(epd)
    get_main_writer().write_f("MinimapPing(")
    write_location(m.locid1)
    get_main_writer().write_f(")")


@EUDFunc
def _writeTalkingPortrait(epd):
    m = _actmap(epd)
    get_main_writer().write_f("TalkingPortrait(")
    write_unit(m.unitid)
    get_main_writer().write_f(", ")
    get_main_writer().write_decimal(m.time)
    get_main_writer().write_f(")")


@EUDFunc
def _writeMuteUnitSpeech(epd):
    get_main_writer().write_f("MuteUnitSpeech()")

@EUDFunc
def _writeUnMuteUnitSpeech(epd):
    get_main_writer().write_f("UnMuteUnitSpeech()")

@EUDFunc
def _writeLeaderBoardComputerPlayers(epd):
    m = _actmap(epd)
    get_main_writer().write_f("LeaderBoardComputerPlayers(")
    write_constant(EPD(tb.PropState), m.amount)
    get_main_writer().write_f(")")


@EUDFunc
def _writeLeaderBoardGoalControl(epd):
    m = _actmap(epd)
    get_main_writer().write_f("LeaderBoardGoalControl(")
    get_main_writer().write_decimal(m.player2)
    get_main_writer().write_f(", ")
    write_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_string(m.strid)
    get_main_writer().write_f(")")


@EUDFunc
def _writeLeaderBoardGoalControlAt(epd):
    m = _actmap(epd)
    get_main_writer().write_f("LeaderBoardGoalControlAt(")
    get_main_writer().write_decimal(m.player2)
    get_main_writer().write_f(", ")
    write_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_location(m.locid1)
    get_main_writer().write_f(", ")
    write_string(m.strid)
    get_main_writer().write_f(")")


@EUDFunc
def _writeLeaderBoardGoalResources(epd):
    m = _actmap(epd)
    get_main_writer().write_f("LeaderBoardGoalResources(")
    get_main_writer().write_decimal(m.player2)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Resource), m.unitid)
    get_main_writer().write_f(", ")
    write_string(m.strid)
    get_main_writer().write_f(")")


@EUDFunc
def _writeLeaderBoardGoalKills(epd):
    m = _actmap(epd)
    get_main_writer().write_f("LeaderBoardGoalKills(")
    get_main_writer().write_decimal(m.player2)
    get_main_writer().write_f(", ")
    write_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_string(m.strid)
    get_main_writer().write_f(")")


@EUDFunc
def _writeLeaderBoardGoalScore(epd):
    m = _actmap(epd)
    get_main_writer().write_f("LeaderBoardGoalScore(")
    get_main_writer().write_decimal(m.player2)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Score), m.unitid)
    get_main_writer().write_f(", ")
    write_string(m.strid)
    get_main_writer().write_f(")")


@EUDFunc
def _writeMoveLocation(epd):
    m = _actmap(epd)
    get_main_writer().write_f("MoveLocation(")
    write_location(m.player2)
    get_main_writer().write_f(", ")
    write_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Player), m.player1)
    get_main_writer().write_f(", ")
    write_location(m.locid1)
    get_main_writer().write_f(")")


@EUDFunc
def _writeMoveUnit(epd):
    m = _actmap(epd)
    get_main_writer().write_f("MoveUnit(")
    if EUDIf()(m.amount == 0):
        get_main_writer().write_f("All")
    if EUDElse()():
        get_main_writer().write_decimal(m.amount)
    EUDEndIf()
    get_main_writer().write_f(", ")
    write_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Player), m.player1)
    get_main_writer().write_f(", ")
    write_location(m.locid1)
    get_main_writer().write_f(", ")
    write_location(m.player2)
    get_main_writer().write_f(")")


@EUDFunc
def _writeLeaderBoardGreed(epd):
    m = _actmap(epd)
    get_main_writer().write_f("LeaderBoardGreed(")
    get_main_writer().write_decimal(m.player2)
    get_main_writer().write_f(")")


@EUDFunc
def _writeSetNextScenario(epd):
    m = _actmap(epd)
    get_main_writer().write_f("SetNextScenario(")
    write_string(m.strid)
    get_main_writer().write_f(")")


@EUDFunc
def _writeSetDoodadState(epd):
    m = _actmap(epd)
    get_main_writer().write_f("SetDoodadState(")
    write_constant(EPD(tb.PropState), m.amount)
    get_main_writer().write_f(", ")
    write_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Player), m.player1)
    get_main_writer().write_f(", ")
    write_location(m.locid1)
    get_main_writer().write_f(")")


@EUDFunc
def _writeSetInvincibility(epd):
    m = _actmap(epd)
    get_main_writer().write_f("SetInvincibility(")
    write_constant(EPD(tb.PropState), m.amount)
    get_main_writer().write_f(", ")
    write_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Player), m.player1)
    get_main_writer().write_f(", ")
    write_location(m.locid1)
    get_main_writer().write_f(")")


@EUDFunc
def _writeCreateUnit(epd):
    m = _actmap(epd)
    get_main_writer().write_f("CreateUnit(")
    get_main_writer().write_decimal(m.amount)
    get_main_writer().write_f(", ")
    write_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_location(m.locid1)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Player), m.player1)
    get_main_writer().write_f(")")


@EUDFunc
def _writeSetDeaths(epd):
    m = _actmap(epd)

    # consider EUD
    if EUDIf()(EUDOr(
            [m.player1 >= 27, m.unitid < 228],
            [m.player1 < 12, m.unitid >= 228],
            [m.internal == 0x4353])):
        # check EUDX
        if EUDIf()(m.internal == 0x4353): # eudx
            get_main_writer().write_f("SetMemoryX(%H, ",
                                      0x58A364 + 4*m.player1 + 48*m.unitid)
            write_constant(EPD(tb.Modifier), m.amount)
            get_main_writer().write_f(", %H(=%D), %H)", m.player2, m.player2, m.locid1)
        if EUDElse()():
            get_main_writer().write_f("SetMemory(%H, ",
                                      0x58A364 + 4*m.player1 + 48*m.unitid)
            write_constant(EPD(tb.Modifier), m.amount)
            get_main_writer().write_f(", %H(=%D))", m.player2, m.player2)
        EUDEndIf()
    if EUDElse()():
        get_main_writer().write_f("SetDeaths(")
        write_constant(EPD(tb.Player), m.player1)
        get_main_writer().write_f(", ")
        write_constant(EPD(tb.Modifier), m.amount)
        get_main_writer().write_f(", ")
        get_main_writer().write_decimal(m.player2)
        get_main_writer().write_f(", ")
        write_unit(m.unitid)
        get_main_writer().write_f(")")
    EUDEndIf()

@EUDFunc
def _writeOrder(epd):
    m = _actmap(epd)
    get_main_writer().write_f("Order(")
    write_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Player), m.player1)
    get_main_writer().write_f(", ")
    write_location(m.locid1)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Order), m.amount)
    get_main_writer().write_f(", ")
    write_location(m.player2)
    get_main_writer().write_f(")")


@EUDFunc
def _writeComment(epd):
    m = _actmap(epd)
    get_main_writer().write_f("Comment(")
    write_string(m.strid)
    get_main_writer().write_f(")")


@EUDFunc
def _writeGiveUnits(epd):
    m = _actmap(epd)
    get_main_writer().write_f("GiveUnits(")
    if EUDIf()(m.amount == 0):
        get_main_writer().write_f("All")
    if EUDElse()():
        get_main_writer().write_decimal(m.amount)
    EUDEndIf()
    get_main_writer().write_f(", ")
    write_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Player), m.player1)
    get_main_writer().write_f(", ")
    write_location(m.locid1)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Player), m.player2)
    get_main_writer().write_f(")")


@EUDFunc
def _writeModifyUnitHitPoints(epd):
    m = _actmap(epd)
    get_main_writer().write_f("ModifyUnitHitPoints(")
    if EUDIf()(m.amount == 0):
        get_main_writer().write_f("All")
    if EUDElse()():
        get_main_writer().write_decimal(m.amount)
    EUDEndIf()
    get_main_writer().write_f(", ")
    write_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Player), m.player1)
    get_main_writer().write_f(", ")
    write_location(m.locid1)
    get_main_writer().write_f(", ")
    get_main_writer().write_decimal(m.player2)
    get_main_writer().write_f(")")


@EUDFunc
def _writeModifyUnitEnergy(epd):
    m = _actmap(epd)
    get_main_writer().write_f("ModifyUnitEnergy(")
    if EUDIf()(m.amount == 0):
        get_main_writer().write_f("All")
    if EUDElse()():
        get_main_writer().write_decimal(m.amount)
    EUDEndIf()
    get_main_writer().write_f(", ")
    write_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Player), m.player1)
    get_main_writer().write_f(", ")
    write_location(m.locid1)
    get_main_writer().write_f(", ")
    get_main_writer().write_decimal(m.player2)
    get_main_writer().write_f(")")


@EUDFunc
def _writeModifyUnitShields(epd):
    m = _actmap(epd)
    get_main_writer().write_f("ModifyUnitShields(")
    if EUDIf()(m.amount == 0):
        get_main_writer().write_f("All")
    if EUDElse()():
        get_main_writer().write_decimal(m.amount)
    EUDEndIf()
    get_main_writer().write_f(", ")
    write_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Player), m.player1)
    get_main_writer().write_f(", ")
    write_location(m.locid1)
    get_main_writer().write_f(", ")
    get_main_writer().write_decimal(m.player2)
    get_main_writer().write_f(")")


@EUDFunc
def _writeModifyUnitResourceAmount(epd):
    m = _actmap(epd)
    get_main_writer().write_f("ModifyUnitResourceAmount(")
    if EUDIf()(m.amount == 0):
        get_main_writer().write_f("All")
    if EUDElse()():
        get_main_writer().write_decimal(m.amount)
    EUDEndIf()
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Player), m.player1)
    get_main_writer().write_f(", ")
    write_location(m.locid1)
    get_main_writer().write_f(", ")
    get_main_writer().write_decimal(m.player2)
    get_main_writer().write_f(")")


@EUDFunc
def _writeModifyUnitHangarCount(epd):
    m = _actmap(epd)
    get_main_writer().write_f("ModifyUnitHangarCount(")
    get_main_writer().write_decimal(m.player2)
    get_main_writer().write_f(", ")
    if EUDIf()(m.amount == 0):
        get_main_writer().write_f("All")
    if EUDElse()():
        get_main_writer().write_decimal(m.amount)
    EUDEndIf()
    get_main_writer().write_f(", ")
    write_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.Player), m.player1)
    get_main_writer().write_f(", ")
    write_location(m.locid1)
    get_main_writer().write_f(")")


@EUDFunc
def _writePauseTimer(epd):
    get_main_writer().write_f("PauseTimer()")

@EUDFunc
def _writeUnpauseTimer(epd):
    get_main_writer().write_f("UnpauseTimer()")

@EUDFunc
def _writeDraw(epd):
    get_main_writer().write_f("Draw()")

@EUDFunc
def _writeSetAllianceStatus(epd):
    m = _actmap(epd)
    get_main_writer().write_f("SetAllianceStatus(")
    write_constant(EPD(tb.Player), m.player1)
    get_main_writer().write_f(", ")
    write_constant(EPD(tb.AllyStatus), m.unitid)
    get_main_writer().write_f(")")
