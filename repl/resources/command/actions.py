from eudplib import *
from ..encoder.const import (
	argEncNumber,
	argEncCount,
	argEncModifier,
	argEncAllyStatus,
	argEncComparison,
	argEncOrder,
	argEncPlayer,
	argEncPropState,
	argEncResource,
	argEncScore,
	argEncSwitchAction,
	argEncSwitchState,
)
from ..encoder.str import (
	argEncUnit,
	argEncLocation,
	argEncAIScript,
	argEncSwitch,
	argEncString,
)
from ...core.command import EUDCommand
from ..table.tables import RegisterCommand
# Note, 
# 1. DisplayText ~ AlwaysDisplay
# 2. UnitProperty is not able to be parsed
# 3. Transmission.. trouble due to two string encoders.

def register_all_actioncmds():

	RegisterCommand('Victory', cmd_Victory)
	RegisterCommand('Defeat', cmd_Defeat)
	RegisterCommand('PreserveTrigger', cmd_PreserveTrigger)
	RegisterCommand('Wait', cmd_Wait)
	RegisterCommand('PauseGame', cmd_PauseGame)
	RegisterCommand('UnpauseGame', cmd_UnpauseGame)
	RegisterCommand('PlayWAV', cmd_PlayWAV)
	RegisterCommand('DisplayText', cmd_DisplayText)
	RegisterCommand('DisplayText_ad', cmd_DisplayText_ad)
	RegisterCommand('CenterView', cmd_CenterView)
	RegisterCommand('CreateUnitWithProperties', cmd_CreateUnitWithProperties)
	RegisterCommand('SetMissionObjectives', cmd_SetMissionObjectives)
	RegisterCommand('SetSwitch', cmd_SetSwitch)
	RegisterCommand('SetCountdownTimer', cmd_SetCountdownTimer)
	RegisterCommand('RunAIScript', cmd_RunAIScript)
	RegisterCommand('RunAIScriptAt', cmd_RunAIScriptAt)
	RegisterCommand('LeaderBoardControl', cmd_LeaderBoardControl)
	RegisterCommand('LeaderBoardControlAt', cmd_LeaderBoardControlAt)
	RegisterCommand('LeaderBoardResources', cmd_LeaderBoardResources)
	RegisterCommand('LeaderBoardKills', cmd_LeaderBoardKills)
	RegisterCommand('LeaderBoardScore', cmd_LeaderBoardScore)
	RegisterCommand('KillUnit', cmd_KillUnit)
	RegisterCommand('KillUnitAt', cmd_KillUnitAt)
	RegisterCommand('RemoveUnit', cmd_RemoveUnit)
	RegisterCommand('RemoveUnitAt', cmd_RemoveUnitAt)
	RegisterCommand('SetResources', cmd_SetResources)
	RegisterCommand('SetScore', cmd_SetScore)
	RegisterCommand('MinimapPing', cmd_MinimapPing)
	RegisterCommand('TalkingPortrait', cmd_TalkingPortrait)
	RegisterCommand('MuteUnitSpeech', cmd_MuteUnitSpeech)
	RegisterCommand('UnMuteUnitSpeech', cmd_UnMuteUnitSpeech)
	RegisterCommand('LeaderBoardComputerPlayers', cmd_LeaderBoardComputerPlayers)
	RegisterCommand('LeaderBoardGoalControl', cmd_LeaderBoardGoalControl)
	RegisterCommand('LeaderBoardGoalControlAt', cmd_LeaderBoardGoalControlAt)
	RegisterCommand('LeaderBoardGoalResources', cmd_LeaderBoardGoalResources)
	RegisterCommand('LeaderBoardGoalKills', cmd_LeaderBoardGoalKills)
	RegisterCommand('LeaderBoardGoalScore', cmd_LeaderBoardGoalScore)
	RegisterCommand('MoveLocation', cmd_MoveLocation)
	RegisterCommand('MoveUnit', cmd_MoveUnit)
	RegisterCommand('LeaderBoardGreed', cmd_LeaderBoardGreed)
	RegisterCommand('SetNextScenario', cmd_SetNextScenario)
	RegisterCommand('SetDoodadState', cmd_SetDoodadState)
	RegisterCommand('SetInvincibility', cmd_SetInvincibility)
	RegisterCommand('CreateUnit', cmd_CreateUnit)
	RegisterCommand('SetDeaths', cmd_SetDeaths)
	RegisterCommand('Order', cmd_Order)
	RegisterCommand('Comment', cmd_Comment)
	RegisterCommand('GiveUnits', cmd_GiveUnits)
	RegisterCommand('ModifyUnitHitPoints', cmd_ModifyUnitHitPoints)
	RegisterCommand('ModifyUnitEnergy', cmd_ModifyUnitEnergy)
	RegisterCommand('ModifyUnitShields', cmd_ModifyUnitShields)
	RegisterCommand('ModifyUnitResourceAmount', cmd_ModifyUnitResourceAmount)
	RegisterCommand('ModifyUnitHangarCount', cmd_ModifyUnitHangarCount)
	RegisterCommand('PauseTimer', cmd_PauseTimer)
	RegisterCommand('UnpauseTimer', cmd_UnpauseTimer)
	RegisterCommand('Draw', cmd_Draw)
	RegisterCommand('SetAllianceStatus', cmd_SetAllianceStatus)
	RegisterCommand('SetMemory', cmd_SetMemory)
	RegisterCommand('SetMemoryEPD', cmd_SetMemoryEPD)
	RegisterCommand('SetDeathsX', cmd_SetDeathsX)
	RegisterCommand('SetMemoryX', cmd_SetMemoryX)

@EUDCommand([])
def cmd_Victory():
	DoActions(Victory())

@EUDCommand([])
def cmd_Defeat():
	DoActions(Defeat())

@EUDCommand([])
def cmd_PreserveTrigger():
	DoActions(PreserveTrigger())

@EUDCommand([argEncNumber])
def cmd_Wait(Time):
	DoActions(Wait(Time))

@EUDCommand([])
def cmd_PauseGame():
	DoActions(PauseGame())

@EUDCommand([])
def cmd_UnpauseGame():
	DoActions(UnpauseGame())

@EUDCommand([argEncString])
def cmd_PlayWAV(WAVName):
	DoActions(PlayWAV(WAVName))

@EUDCommand([argEncString])
def cmd_DisplayText(Text):
	DoActions(DisplayText(Text))

@EUDCommand([argEncString, argEncNumber])
def cmd_DisplayText_ad(Text, AlwaysDisplay):
	DoActions(DisplayText(Text, AlwaysDisplay))

@EUDCommand([argEncLocation])
def cmd_CenterView(Where):
	DoActions(CenterView(Where))

# UnitProperty!
@EUDCommand([argEncNumber, argEncUnit, argEncLocation, argEncPlayer, argEncNumber])
def cmd_CreateUnitWithProperties(Count, Unit, Where, Player, Properties):
	DoActions(Action(Where, 0, 0, 0, Player, Properties, Unit, 11, Count, 28))

@EUDCommand([argEncString])
def cmd_SetMissionObjectives(Text):
	DoActions(SetMissionObjectives(Text))

@EUDCommand([argEncSwitch, argEncSwitchAction])
def cmd_SetSwitch(Switch, State):
	DoActions(SetSwitch(Switch, State))

@EUDCommand([argEncModifier, argEncNumber])
def cmd_SetCountdownTimer(TimeModifier, Time):
	DoActions(SetCountdownTimer(TimeModifier, Time))

@EUDCommand([argEncAIScript])
def cmd_RunAIScript(Script):
	DoActions(RunAIScript(Script))

@EUDCommand([argEncAIScript, argEncLocation])
def cmd_RunAIScriptAt(Script, Where):
	DoActions(RunAIScriptAt(Script, Where))

@EUDCommand([argEncUnit, argEncString])
def cmd_LeaderBoardControl(Unit, Label):
	DoActions(LeaderBoardControl(Unit, Label))

@EUDCommand([argEncUnit, argEncLocation, argEncString])
def cmd_LeaderBoardControlAt(Unit, Location, Label):
	DoActions(LeaderBoardControlAt(Unit, Location, Label))

@EUDCommand([argEncResource, argEncString])
def cmd_LeaderBoardResources(ResourceType, Label):
	DoActions(LeaderBoardResources(ResourceType, Label))

@EUDCommand([argEncUnit, argEncString])
def cmd_LeaderBoardKills(Unit, Label):
	DoActions(LeaderBoardKills(Unit, Label))

@EUDCommand([argEncScore, argEncString])
def cmd_LeaderBoardScore(ScoreType, Label):
	DoActions(LeaderBoardScore(ScoreType, Label))

@EUDCommand([argEncUnit, argEncPlayer])
def cmd_KillUnit(Unit, Player):
	DoActions(KillUnit(Unit, Player))

@EUDCommand([argEncCount, argEncUnit, argEncLocation, argEncPlayer])
def cmd_KillUnitAt(Count, Unit, Where, ForPlayer):
	DoActions(KillUnitAt(Count, Unit, Where, ForPlayer))

@EUDCommand([argEncUnit, argEncPlayer])
def cmd_RemoveUnit(Unit, Player):
	DoActions(RemoveUnit(Unit, Player))

@EUDCommand([argEncCount, argEncUnit, argEncLocation, argEncPlayer])
def cmd_RemoveUnitAt(Count, Unit, Where, ForPlayer):
	DoActions(RemoveUnitAt(Count, Unit, Where, ForPlayer))

@EUDCommand([argEncPlayer, argEncModifier, argEncNumber, argEncResource])
def cmd_SetResources(Player, Modifier, Amount, ResourceType):
	DoActions(SetResources(Player, Modifier, Amount, ResourceType))

@EUDCommand([argEncPlayer, argEncModifier, argEncNumber, argEncScore])
def cmd_SetScore(Player, Modifier, Amount, ScoreType):
	DoActions(SetScore(Player, Modifier, Amount, ScoreType))

@EUDCommand([argEncLocation])
def cmd_MinimapPing(Where):
	DoActions(MinimapPing(Where))

@EUDCommand([argEncUnit, argEncNumber])
def cmd_TalkingPortrait(Unit, Time):
	DoActions(TalkingPortrait(Unit, Time))

@EUDCommand([])
def cmd_MuteUnitSpeech():
	DoActions(MuteUnitSpeech())

@EUDCommand([])
def cmd_UnMuteUnitSpeech():
	DoActions(UnMuteUnitSpeech())

@EUDCommand([argEncPropState])
def cmd_LeaderBoardComputerPlayers(State):
	DoActions(LeaderBoardComputerPlayers(State))

@EUDCommand([argEncNumber, argEncUnit, argEncString])
def cmd_LeaderBoardGoalControl(Goal, Unit, Label):
	DoActions(LeaderBoardGoalControl(Goal, Unit, Label))

@EUDCommand([argEncNumber, argEncUnit, argEncLocation, argEncString])
def cmd_LeaderBoardGoalControlAt(Goal, Unit, Location, Label):
	DoActions(LeaderBoardGoalControlAt(Goal, Unit, Location, Label))

@EUDCommand([argEncNumber, argEncResource, argEncString])
def cmd_LeaderBoardGoalResources(Goal, ResourceType, Label):
	DoActions(LeaderBoardGoalResources(Goal, ResourceType, Label))

@EUDCommand([argEncNumber, argEncUnit, argEncString])
def cmd_LeaderBoardGoalKills(Goal, Unit, Label):
	DoActions(LeaderBoardGoalKills(Goal, Unit, Label))

@EUDCommand([argEncNumber, argEncScore, argEncString])
def cmd_LeaderBoardGoalScore(Goal, ScoreType, Label):
	DoActions(LeaderBoardGoalScore(Goal, ScoreType, Label))

@EUDCommand([argEncLocation, argEncUnit, argEncPlayer, argEncLocation])
def cmd_MoveLocation(Location, OnUnit, Owner, DestLocation):
	DoActions(MoveLocation(Location, OnUnit, Owner, DestLocation))

@EUDCommand([argEncCount, argEncUnit, argEncPlayer, argEncLocation, argEncLocation])
def cmd_MoveUnit(Count, UnitType, Owner, StartLocation, DestLocation):
	DoActions(MoveUnit(Count, UnitType, Owner, StartLocation, DestLocation))

@EUDCommand([argEncNumber])
def cmd_LeaderBoardGreed(Goal):
	DoActions(LeaderBoardGreed(Goal))

@EUDCommand([argEncString])
def cmd_SetNextScenario(ScenarioName):
	DoActions(SetNextScenario(ScenarioName))

@EUDCommand([argEncPropState, argEncUnit, argEncPlayer, argEncLocation])
def cmd_SetDoodadState(State, Unit, Owner, Where):
	DoActions(SetDoodadState(State, Unit, Owner, Where))

@EUDCommand([argEncPropState, argEncUnit, argEncPlayer, argEncLocation])
def cmd_SetInvincibility(State, Unit, Owner, Where):
	DoActions(SetInvincibility(State, Unit, Owner, Where))

@EUDCommand([argEncNumber, argEncUnit, argEncLocation, argEncPlayer])
def cmd_CreateUnit(Number, Unit, Where, ForPlayer):
	DoActions(CreateUnit(Number, Unit, Where, ForPlayer))

@EUDCommand([argEncPlayer, argEncModifier, argEncNumber, argEncUnit])
def cmd_SetDeaths(Player, Modifier, Number, Unit):
	DoActions(SetDeaths(Player, Modifier, Number, Unit))

@EUDCommand([argEncUnit, argEncPlayer, argEncLocation, argEncOrder, argEncLocation])
def cmd_Order(Unit, Owner, StartLocation, OrderType, DestLocation):
	DoActions(Order(Unit, Owner, StartLocation, OrderType, DestLocation))

@EUDCommand([argEncString])
def cmd_Comment(Text):
	DoActions(Comment(Text))

@EUDCommand([argEncCount, argEncUnit, argEncPlayer, argEncLocation, argEncPlayer])
def cmd_GiveUnits(Count, Unit, Owner, Where, NewOwner):
	DoActions(GiveUnits(Count, Unit, Owner, Where, NewOwner))

@EUDCommand([argEncCount, argEncUnit, argEncPlayer, argEncLocation, argEncNumber])
def cmd_ModifyUnitHitPoints(Count, Unit, Owner, Where, Percent):
	DoActions(ModifyUnitHitPoints(Count, Unit, Owner, Where, Percent))

@EUDCommand([argEncCount, argEncUnit, argEncPlayer, argEncLocation, argEncNumber])
def cmd_ModifyUnitEnergy(Count, Unit, Owner, Where, Percent):
	DoActions(ModifyUnitEnergy(Count, Unit, Owner, Where, Percent))

@EUDCommand([argEncCount, argEncUnit, argEncPlayer, argEncLocation, argEncNumber])
def cmd_ModifyUnitShields(Count, Unit, Owner, Where, Percent):
	DoActions(ModifyUnitShields(Count, Unit, Owner, Where, Percent))

@EUDCommand([argEncNumber, argEncPlayer, argEncLocation, argEncNumber])
def cmd_ModifyUnitResourceAmount(Count, Owner, Where, NewValue):
	DoActions(ModifyUnitResourceAmount(Count, Owner, Where, NewValue))

@EUDCommand([argEncNumber, argEncCount, argEncUnit, argEncPlayer, argEncLocation])
def cmd_ModifyUnitHangarCount(Add, Count, Unit, Owner, Where):
	DoActions(ModifyUnitHangarCount(Add, Count, Unit, Owner, Where))

@EUDCommand([])
def cmd_PauseTimer():
	DoActions(PauseTimer())

@EUDCommand([])
def cmd_UnpauseTimer():
	DoActions(UnpauseTimer())

@EUDCommand([])
def cmd_Draw():
	DoActions(Draw())

@EUDCommand([argEncPlayer, argEncAllyStatus])
def cmd_SetAllianceStatus(Player, Status):
	DoActions(SetAllianceStatus(Player, Status))

@EUDCommand([argEncNumber, argEncModifier, argEncNumber])
def cmd_SetMemory(dest, modtype, value):
	DoActions(SetMemory(dest, modtype, value))

@EUDCommand([argEncPlayer, argEncModifier, argEncNumber])
def cmd_SetMemoryEPD(dest, modtype, value):
	DoActions(SetMemoryEPD(dest, modtype, value))

@EUDCommand([argEncPlayer, argEncModifier, argEncNumber, argEncUnit, argEncNumber])
def cmd_SetDeathsX(Player, Modifier, Number, Unit, Mask):
	DoActions(SetDeathsX(Player, Modifier, Number, Unit, Mask))

@EUDCommand([argEncNumber, argEncModifier, argEncNumber, argEncNumber])
def cmd_SetMemoryX(dest, modtype, value, mask):
	DoActions(SetMemoryX(dest, modtype, value, mask))

