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
from ...core.command import EUDCommand, registerCommand
# Note, 
# 1. DisplayText ~ AlwaysDisplay
# 2. UnitProperty is not able to be parsed
# 3. Transmission.. trouble due to two string encoders.

def register_all_actioncmds():

	registerCommand('Victory', cmd_Victory)
	registerCommand('Defeat', cmd_Defeat)
	registerCommand('PreserveTrigger', cmd_PreserveTrigger)
	registerCommand('Wait', cmd_Wait)
	registerCommand('PauseGame', cmd_PauseGame)
	registerCommand('UnpauseGame', cmd_UnpauseGame)
	registerCommand('PlayWAV', cmd_PlayWAV)
	registerCommand('DisplayText', cmd_DisplayText)
	registerCommand('DisplayText_ad', cmd_DisplayText_ad)
	registerCommand('CenterView', cmd_CenterView)
	registerCommand('CreateUnitWithProperties', cmd_CreateUnitWithProperties)
	registerCommand('SetMissionObjectives', cmd_SetMissionObjectives)
	registerCommand('SetSwitch', cmd_SetSwitch)
	registerCommand('SetCountdownTimer', cmd_SetCountdownTimer)
	registerCommand('RunAIScript', cmd_RunAIScript)
	registerCommand('RunAIScriptAt', cmd_RunAIScriptAt)
	registerCommand('LeaderBoardControl', cmd_LeaderBoardControl)
	registerCommand('LeaderBoardControlAt', cmd_LeaderBoardControlAt)
	registerCommand('LeaderBoardResources', cmd_LeaderBoardResources)
	registerCommand('LeaderBoardKills', cmd_LeaderBoardKills)
	registerCommand('LeaderBoardScore', cmd_LeaderBoardScore)
	registerCommand('KillUnit', cmd_KillUnit)
	registerCommand('KillUnitAt', cmd_KillUnitAt)
	registerCommand('RemoveUnit', cmd_RemoveUnit)
	registerCommand('RemoveUnitAt', cmd_RemoveUnitAt)
	registerCommand('SetResources', cmd_SetResources)
	registerCommand('SetScore', cmd_SetScore)
	registerCommand('MinimapPing', cmd_MinimapPing)
	registerCommand('TalkingPortrait', cmd_TalkingPortrait)
	registerCommand('MuteUnitSpeech', cmd_MuteUnitSpeech)
	registerCommand('UnMuteUnitSpeech', cmd_UnMuteUnitSpeech)
	registerCommand('LeaderBoardComputerPlayers', cmd_LeaderBoardComputerPlayers)
	registerCommand('LeaderBoardGoalControl', cmd_LeaderBoardGoalControl)
	registerCommand('LeaderBoardGoalControlAt', cmd_LeaderBoardGoalControlAt)
	registerCommand('LeaderBoardGoalResources', cmd_LeaderBoardGoalResources)
	registerCommand('LeaderBoardGoalKills', cmd_LeaderBoardGoalKills)
	registerCommand('LeaderBoardGoalScore', cmd_LeaderBoardGoalScore)
	registerCommand('MoveLocation', cmd_MoveLocation)
	registerCommand('MoveUnit', cmd_MoveUnit)
	registerCommand('LeaderBoardGreed', cmd_LeaderBoardGreed)
	registerCommand('SetNextScenario', cmd_SetNextScenario)
	registerCommand('SetDoodadState', cmd_SetDoodadState)
	registerCommand('SetInvincibility', cmd_SetInvincibility)
	registerCommand('CreateUnit', cmd_CreateUnit)
	registerCommand('SetDeaths', cmd_SetDeaths)
	registerCommand('Order', cmd_Order)
	registerCommand('Comment', cmd_Comment)
	registerCommand('GiveUnits', cmd_GiveUnits)
	registerCommand('ModifyUnitHitPoints', cmd_ModifyUnitHitPoints)
	registerCommand('ModifyUnitEnergy', cmd_ModifyUnitEnergy)
	registerCommand('ModifyUnitShields', cmd_ModifyUnitShields)
	registerCommand('ModifyUnitResourceAmount', cmd_ModifyUnitResourceAmount)
	registerCommand('ModifyUnitHangarCount', cmd_ModifyUnitHangarCount)
	registerCommand('PauseTimer', cmd_PauseTimer)
	registerCommand('UnpauseTimer', cmd_UnpauseTimer)
	registerCommand('Draw', cmd_Draw)
	registerCommand('SetAllianceStatus', cmd_SetAllianceStatus)
	registerCommand('SetMemory', cmd_SetMemory)
	registerCommand('SetMemoryEPD', cmd_SetMemoryEPD)
	registerCommand('SetDeathsX', cmd_SetDeathsX)
	registerCommand('SetMemoryX', cmd_SetMemoryX)

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

