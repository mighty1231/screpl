"""Add methods on REPLByteRW to write trigger actions"""

from eudplib import *
from screpl.resources.table import tables as tb

def writer_action_init():
    """Add a method on REPLByteRW"""
    from screpl.utils.byterw import REPLByteRW

    REPLByteRW.add_method(write_action_epd)

action_epd_offset_map = EPDOffsetMap((
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

@EUDMethod
def write_action_epd(self, epd):
    """Write trigger action with eudplib syntax"""

    write_mtds = [
        (1, _write__Victory),
        (2, _write__Defeat),
        (3, _write__PreserveTrigger),
        (4, _write__Wait),
        (5, _write__PauseGame),
        (6, _write__UnpauseGame),
        (7, _write__Transmission),
        (8, _write__PlayWAV),
        (9, _write__DisplayText),
        (10, _write__CenterView),
        (11, _write__CreateUnitWithProperties),
        (12, _write__SetMissionObjectives),
        (13, _write__SetSwitch),
        (14, _write__SetCountdownTimer),
        (15, _write__RunAIScript),
        (16, _write__RunAIScriptAt),
        (17, _write__LeaderBoardControl),
        (18, _write__LeaderBoardControlAt),
        (19, _write__LeaderBoardResources),
        (20, _write__LeaderBoardKills),
        (21, _write__LeaderBoardScore),
        (22, _write__KillUnit),
        (23, _write__KillUnitAt),
        (24, _write__RemoveUnit),
        (25, _write__RemoveUnitAt),
        (26, _write__SetResources),
        (27, _write__SetScore),
        (28, _write__MinimapPing),
        (29, _write__TalkingPortrait),
        (30, _write__MuteUnitSpeech),
        (31, _write__UnMuteUnitSpeech),
        (32, _write__LeaderBoardComputerPlayers),
        (33, _write__LeaderBoardGoalControl),
        (34, _write__LeaderBoardGoalControlAt),
        (35, _write__LeaderBoardGoalResources),
        (36, _write__LeaderBoardGoalKills),
        (37, _write__LeaderBoardGoalScore),
        (38, _write__MoveLocation),
        (39, _write__MoveUnit),
        (40, _write__LeaderBoardGreed),
        (41, _write__SetNextScenario),
        (42, _write__SetDoodadState),
        (43, _write__SetInvincibility),
        (44, _write__CreateUnit),
        (45, _write__SetDeaths),
        (46, _write__Order),
        (47, _write__Comment),
        (48, _write__GiveUnits),
        (49, _write__ModifyUnitHitPoints),
        (50, _write__ModifyUnitEnergy),
        (51, _write__ModifyUnitShields),
        (52, _write__ModifyUnitResourceAmount),
        (53, _write__ModifyUnitHangarCount),
        (54, _write__PauseTimer),
        (55, _write__UnpauseTimer),
        (56, _write__Draw),
        (57, _write__SetAllianceStatus)]

    act = action_epd_offset_map(epd)
    acttype = act.acttype
    EUDSwitch(acttype)
    for mtd_id, mtd in write_mtds:
        EUDSwitchCase()(mtd_id)
        mtd(self, epd)
        EUDBreak()
    if EUDSwitchDefault()():
        self.write_f(
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
    EUDEndSwitch()

    # additional flags
    flags = act.flags
    if EUDIf()(flags.ExactlyX(1, 1)):
        self.write_f(' WaitExecute')
    EUDEndIf()
    if EUDIf()(flags.ExactlyX(2, 2)):
        self.write_f(' IgnoreExecution')
    EUDEndIf()
    if EUDIf()(flags.ExactlyX(4, 4)):
        self.write_f(' AlwaysDisplay')
    EUDEndIf()

@EUDMethod
def _write__Victory(self, epd):
    self.write_f("Victory()")

@EUDMethod
def _write__Defeat(self, epd):
    self.write_f("Defeat()")

@EUDMethod
def _write__PreserveTrigger(self, epd):
    self.write_f("PreserveTrigger()")

@EUDMethod
def _write__Wait(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("Wait(")
    self.write_decimal(m.time)
    self.write_f(")")

@EUDMethod
def _write__PauseGame(self, epd):
    self.write_f("PauseGame()")

@EUDMethod
def _write__UnpauseGame(self, epd):
    self.write_f("UnpauseGame()")

@EUDMethod
def _write__Transmission(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("Transmission(")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_location(m.locid1)
    self.write_f(", ")
    self.write_string(m.wavid)
    self.write_f(", ")
    self.write_constant(EPD(tb.Modifier), m.amount)
    self.write_f(", ")
    self.write_decimal(m.time)
    self.write_f(", ")
    self.write_string(m.strid)
    self.write_f(")")


@EUDMethod
def _write__PlayWAV(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("PlayWAV(")
    self.write_string(m.wavid)
    self.write_f(")")


@EUDMethod
def _write__DisplayText(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("DisplayText(")
    self.write_string(m.strid)
    self.write_f(")")


@EUDMethod
def _write__CenterView(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("CenterView(")
    self.write_location(m.locid1)
    self.write_f(")")


@EUDMethod
def _write__CreateUnitWithProperties(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("CreateUnitWithProperties(")
    self.write_decimal(m.amount)
    self.write_f(", ")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_location(m.locid1)
    self.write_f(", ")
    self.write_constant(EPD(tb.Player), m.player1)
    self.write_f(", ")
    self.write_decimal(m.player2) # @TODO property
    self.write_f(")")


@EUDMethod
def _write__SetMissionObjectives(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("SetMissionObjectives(")
    self.write_string(m.strid)
    self.write_f(")")


@EUDMethod
def _write__SetSwitch(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("SetSwitch(")
    self.write_switch(m.player2)
    self.write_f(", ")
    self.write_constant(EPD(tb.SwitchAction), m.amount)
    self.write_f(")")


@EUDMethod
def _write__SetCountdownTimer(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("SetCountdownTimer(")
    self.write_constant(EPD(tb.Modifier), m.amount)
    self.write_f(", ")
    self.write_decimal(m.time)
    self.write_f(")")


@EUDMethod
def _write__RunAIScript(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("RunAIScript(")
    self.write_aiscript(m.player2)
    self.write_f(")")


@EUDMethod
def _write__RunAIScriptAt(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("RunAIScriptAt(")
    self.write_aiscript(m.player2)
    self.write_f(", ")
    self.write_location(m.locid1)
    self.write_f(")")


@EUDMethod
def _write__LeaderBoardControl(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("LeaderBoardControl(")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_string(m.strid)
    self.write_f(")")


@EUDMethod
def _write__LeaderBoardControlAt(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("LeaderBoardControlAt(")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_location(m.locid1)
    self.write_f(", ")
    self.write_string(m.strid)
    self.write_f(")")


@EUDMethod
def _write__LeaderBoardResources(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("LeaderBoardResources(")
    self.write_constant(EPD(tb.Resource), m.unitid)
    self.write_f(", ")
    self.write_string(m.strid)
    self.write_f(")")


@EUDMethod
def _write__LeaderBoardKills(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("LeaderBoardKills(")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_string(m.strid)
    self.write_f(")")


@EUDMethod
def _write__LeaderBoardScore(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("LeaderBoardScore(")
    self.write_constant(EPD(tb.Score), m.unitid)
    self.write_f(", ")
    self.write_string(m.strid)
    self.write_f(")")


@EUDMethod
def _write__KillUnit(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("KillUnit(")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_constant(EPD(tb.Player), m.player1)
    self.write_f(")")


@EUDMethod
def _write__KillUnitAt(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("KillUnitAt(")
    if EUDIf()(m.amount == 0):
        self.write_f("All")
    if EUDElse()():
        self.write_decimal(m.amount)
    EUDEndIf()
    self.write_f(", ")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_location(m.locid1)
    self.write_f(", ")
    self.write_constant(EPD(tb.Player), m.player1)
    self.write_f(")")


@EUDMethod
def _write__RemoveUnit(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("RemoveUnit(")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_constant(EPD(tb.Player), m.player1)
    self.write_f(")")


@EUDMethod
def _write__RemoveUnitAt(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("RemoveUnitAt(")
    if EUDIf()(m.amount == 0):
        self.write_f("All")
    if EUDElse()():
        self.write_decimal(m.amount)
    EUDEndIf()
    self.write_f(", ")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_location(m.locid1)
    self.write_f(", ")
    self.write_constant(EPD(tb.Player), m.player1)
    self.write_f(")")


@EUDMethod
def _write__SetResources(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("SetResources(")
    self.write_constant(EPD(tb.Player), m.player1)
    self.write_f(", ")
    self.write_constant(EPD(tb.Modifier), m.amount)
    self.write_f(", ")
    self.write_decimal(m.player2)
    self.write_f(", ")
    self.write_constant(EPD(tb.Resource), m.unitid)
    self.write_f(")")


@EUDMethod
def _write__SetScore(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("SetScore(")
    self.write_constant(EPD(tb.Player), m.player1)
    self.write_f(", ")
    self.write_constant(EPD(tb.Modifier), m.amount)
    self.write_f(", ")
    self.write_decimal(m.player2)
    self.write_f(", ")
    self.write_constant(EPD(tb.Score), m.unitid)
    self.write_f(")")


@EUDMethod
def _write__MinimapPing(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("MinimapPing(")
    self.write_location(m.locid1)
    self.write_f(")")


@EUDMethod
def _write__TalkingPortrait(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("TalkingPortrait(")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_decimal(m.time)
    self.write_f(")")


@EUDMethod
def _write__MuteUnitSpeech(self, epd):
    self.write_f("MuteUnitSpeech()")

@EUDMethod
def _write__UnMuteUnitSpeech(self, epd):
    self.write_f("UnMuteUnitSpeech()")

@EUDMethod
def _write__LeaderBoardComputerPlayers(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("LeaderBoardComputerPlayers(")
    self.write_constant(EPD(tb.PropState), m.amount)
    self.write_f(")")


@EUDMethod
def _write__LeaderBoardGoalControl(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("LeaderBoardGoalControl(")
    self.write_decimal(m.player2)
    self.write_f(", ")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_string(m.strid)
    self.write_f(")")


@EUDMethod
def _write__LeaderBoardGoalControlAt(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("LeaderBoardGoalControlAt(")
    self.write_decimal(m.player2)
    self.write_f(", ")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_location(m.locid1)
    self.write_f(", ")
    self.write_string(m.strid)
    self.write_f(")")


@EUDMethod
def _write__LeaderBoardGoalResources(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("LeaderBoardGoalResources(")
    self.write_decimal(m.player2)
    self.write_f(", ")
    self.write_constant(EPD(tb.Resource), m.unitid)
    self.write_f(", ")
    self.write_string(m.strid)
    self.write_f(")")


@EUDMethod
def _write__LeaderBoardGoalKills(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("LeaderBoardGoalKills(")
    self.write_decimal(m.player2)
    self.write_f(", ")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_string(m.strid)
    self.write_f(")")


@EUDMethod
def _write__LeaderBoardGoalScore(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("LeaderBoardGoalScore(")
    self.write_decimal(m.player2)
    self.write_f(", ")
    self.write_constant(EPD(tb.Score), m.unitid)
    self.write_f(", ")
    self.write_string(m.strid)
    self.write_f(")")


@EUDMethod
def _write__MoveLocation(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("MoveLocation(")
    self.write_location(m.player2)
    self.write_f(", ")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_constant(EPD(tb.Player), m.player1)
    self.write_f(", ")
    self.write_location(m.locid1)
    self.write_f(")")


@EUDMethod
def _write__MoveUnit(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("MoveUnit(")
    if EUDIf()(m.amount == 0):
        self.write_f("All")
    if EUDElse()():
        self.write_decimal(m.amount)
    EUDEndIf()
    self.write_f(", ")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_constant(EPD(tb.Player), m.player1)
    self.write_f(", ")
    self.write_location(m.locid1)
    self.write_f(", ")
    self.write_location(m.player2)
    self.write_f(")")


@EUDMethod
def _write__LeaderBoardGreed(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("LeaderBoardGreed(")
    self.write_decimal(m.player2)
    self.write_f(")")


@EUDMethod
def _write__SetNextScenario(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("SetNextScenario(")
    self.write_string(m.strid)
    self.write_f(")")


@EUDMethod
def _write__SetDoodadState(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("SetDoodadState(")
    self.write_constant(EPD(tb.PropState), m.amount)
    self.write_f(", ")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_constant(EPD(tb.Player), m.player1)
    self.write_f(", ")
    self.write_location(m.locid1)
    self.write_f(")")


@EUDMethod
def _write__SetInvincibility(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("SetInvincibility(")
    self.write_constant(EPD(tb.PropState), m.amount)
    self.write_f(", ")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_constant(EPD(tb.Player), m.player1)
    self.write_f(", ")
    self.write_location(m.locid1)
    self.write_f(")")


@EUDMethod
def _write__CreateUnit(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("CreateUnit(")
    self.write_decimal(m.amount)
    self.write_f(", ")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_location(m.locid1)
    self.write_f(", ")
    self.write_constant(EPD(tb.Player), m.player1)
    self.write_f(")")


@EUDMethod
def _write__SetDeaths(self, epd):
    m = action_epd_offset_map(epd)

    # consider EUD
    if EUDIf()(EUDOr([m.player1 >= 27, m.unitid < 228],
                     [m.player1 < 12, m.unitid >= 228],
                     [m.internal == 0x4353])):
        # check EUDX
        if EUDIf()(m.internal == 0x4353): # eudx
            self.write_f("SetMemoryX(%H, ",
                         0x58A364 + 4*m.player1 + 48*m.unitid)
            self.write_constant(EPD(tb.Modifier), m.amount)
            self.write_f(", %H(=%D), %H)", m.player2, m.player2, m.locid1)
        if EUDElse()():
            self.write_f("SetMemory(%H, ",
                         0x58A364 + 4*m.player1 + 48*m.unitid)
            self.write_constant(EPD(tb.Modifier), m.amount)
            self.write_f(", %H(=%D))", m.player2, m.player2)
        EUDEndIf()
    if EUDElse()():
        self.write_f("SetDeaths(")
        self.write_constant(EPD(tb.Player), m.player1)
        self.write_f(", ")
        self.write_constant(EPD(tb.Modifier), m.amount)
        self.write_f(", ")
        self.write_decimal(m.player2)
        self.write_f(", ")
        self.write_unit(m.unitid)
        self.write_f(")")
    EUDEndIf()

@EUDMethod
def _write__Order(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("Order(")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_constant(EPD(tb.Player), m.player1)
    self.write_f(", ")
    self.write_location(m.locid1)
    self.write_f(", ")
    self.write_constant(EPD(tb.Order), m.amount)
    self.write_f(", ")
    self.write_location(m.player2)
    self.write_f(")")


@EUDMethod
def _write__Comment(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("Comment(")
    self.write_string(m.strid)
    self.write_f(")")


@EUDMethod
def _write__GiveUnits(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("GiveUnits(")
    if EUDIf()(m.amount == 0):
        self.write_f("All")
    if EUDElse()():
        self.write_decimal(m.amount)
    EUDEndIf()
    self.write_f(", ")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_constant(EPD(tb.Player), m.player1)
    self.write_f(", ")
    self.write_location(m.locid1)
    self.write_f(", ")
    self.write_constant(EPD(tb.Player), m.player2)
    self.write_f(")")


@EUDMethod
def _write__ModifyUnitHitPoints(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("ModifyUnitHitPoints(")
    if EUDIf()(m.amount == 0):
        self.write_f("All")
    if EUDElse()():
        self.write_decimal(m.amount)
    EUDEndIf()
    self.write_f(", ")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_constant(EPD(tb.Player), m.player1)
    self.write_f(", ")
    self.write_location(m.locid1)
    self.write_f(", ")
    self.write_decimal(m.player2)
    self.write_f(")")


@EUDMethod
def _write__ModifyUnitEnergy(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("ModifyUnitEnergy(")
    if EUDIf()(m.amount == 0):
        self.write_f("All")
    if EUDElse()():
        self.write_decimal(m.amount)
    EUDEndIf()
    self.write_f(", ")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_constant(EPD(tb.Player), m.player1)
    self.write_f(", ")
    self.write_location(m.locid1)
    self.write_f(", ")
    self.write_decimal(m.player2)
    self.write_f(")")


@EUDMethod
def _write__ModifyUnitShields(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("ModifyUnitShields(")
    if EUDIf()(m.amount == 0):
        self.write_f("All")
    if EUDElse()():
        self.write_decimal(m.amount)
    EUDEndIf()
    self.write_f(", ")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_constant(EPD(tb.Player), m.player1)
    self.write_f(", ")
    self.write_location(m.locid1)
    self.write_f(", ")
    self.write_decimal(m.player2)
    self.write_f(")")


@EUDMethod
def _write__ModifyUnitResourceAmount(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("ModifyUnitResourceAmount(")
    if EUDIf()(m.amount == 0):
        self.write_f("All")
    if EUDElse()():
        self.write_decimal(m.amount)
    EUDEndIf()
    self.write_f(", ")
    self.write_constant(EPD(tb.Player), m.player1)
    self.write_f(", ")
    self.write_location(m.locid1)
    self.write_f(", ")
    self.write_decimal(m.player2)
    self.write_f(")")


@EUDMethod
def _write__ModifyUnitHangarCount(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("ModifyUnitHangarCount(")
    self.write_decimal(m.player2)
    self.write_f(", ")
    if EUDIf()(m.amount == 0):
        self.write_f("All")
    if EUDElse()():
        self.write_decimal(m.amount)
    EUDEndIf()
    self.write_f(", ")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_constant(EPD(tb.Player), m.player1)
    self.write_f(", ")
    self.write_location(m.locid1)
    self.write_f(")")


@EUDMethod
def _write__PauseTimer(self, epd):
    self.write_f("PauseTimer()")

@EUDMethod
def _write__UnpauseTimer(self, epd):
    self.write_f("UnpauseTimer()")

@EUDMethod
def _write__Draw(self, epd):
    self.write_f("Draw()")

@EUDMethod
def _write__SetAllianceStatus(self, epd):
    m = action_epd_offset_map(epd)
    self.write_f("SetAllianceStatus(")
    self.write_constant(EPD(tb.Player), m.player1)
    self.write_f(", ")
    self.write_constant(EPD(tb.AllyStatus), m.unitid)
    self.write_f(")")
