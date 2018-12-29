from eudplib import *
from utils import *
from enc_const import (
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
from enc_str import (
	argEncUnit,
	argEncLocation,
	argEncAIScript,
	argEncSwitch,
	argEncString,
)
from command import EUDCommand, EUDCommandStruct
# Note, 
# 1. DisplayText ~ AlwaysDisplay
# 2. UnitProperty is not able to be parsed
# 3. Transmission byebye

def cmdstruct_all_actions():
	actions = []
	actions.append(EUDCommandStruct('Victory', cmd_Victory))
	actions.append(EUDCommandStruct('Defeat', cmd_Defeat))
	actions.append(EUDCommandStruct('PreserveTrigger', cmd_PreserveTrigger))
	actions.append(EUDCommandStruct('Wait', cmd_Wait))
	actions.append(EUDCommandStruct('PauseGame', cmd_PauseGame))
	actions.append(EUDCommandStruct('UnpauseGame', cmd_UnpauseGame))
	actions.append(EUDCommandStruct('PlayWAV', cmd_PlayWAV))
	actions.append(EUDCommandStruct('DisplayText', cmd_DisplayText))
	actions.append(EUDCommandStruct('DisplayText_ad', cmd_DisplayText_ad))
	actions.append(EUDCommandStruct('CenterView', cmd_CenterView))
	actions.append(EUDCommandStruct('CreateUnitWithProperties', cmd_CreateUnitWithProperties))
	actions.append(EUDCommandStruct('SetMissionObjectives', cmd_SetMissionObjectives))
	actions.append(EUDCommandStruct('SetSwitch', cmd_SetSwitch))
	actions.append(EUDCommandStruct('SetCountdownTimer', cmd_SetCountdownTimer))
	actions.append(EUDCommandStruct('RunAIScript', cmd_RunAIScript))
	actions.append(EUDCommandStruct('RunAIScriptAt', cmd_RunAIScriptAt))
	actions.append(EUDCommandStruct('LeaderBoardControl', cmd_LeaderBoardControl))
	actions.append(EUDCommandStruct('LeaderBoardControlAt', cmd_LeaderBoardControlAt))
	actions.append(EUDCommandStruct('LeaderBoardResources', cmd_LeaderBoardResources))
	actions.append(EUDCommandStruct('LeaderBoardKills', cmd_LeaderBoardKills))
	actions.append(EUDCommandStruct('LeaderBoardScore', cmd_LeaderBoardScore))
	actions.append(EUDCommandStruct('KillUnit', cmd_KillUnit))
	actions.append(EUDCommandStruct('KillUnitAt', cmd_KillUnitAt))
	actions.append(EUDCommandStruct('RemoveUnit', cmd_RemoveUnit))
	actions.append(EUDCommandStruct('RemoveUnitAt', cmd_RemoveUnitAt))
	actions.append(EUDCommandStruct('SetResources', cmd_SetResources))
	actions.append(EUDCommandStruct('SetScore', cmd_SetScore))
	actions.append(EUDCommandStruct('MinimapPing', cmd_MinimapPing))
	actions.append(EUDCommandStruct('TalkingPortrait', cmd_TalkingPortrait))
	actions.append(EUDCommandStruct('MuteUnitSpeech', cmd_MuteUnitSpeech))
	actions.append(EUDCommandStruct('UnMuteUnitSpeech', cmd_UnMuteUnitSpeech))
	actions.append(EUDCommandStruct('LeaderBoardComputerPlayers', cmd_LeaderBoardComputerPlayers))
	actions.append(EUDCommandStruct('LeaderBoardGoalControl', cmd_LeaderBoardGoalControl))
	actions.append(EUDCommandStruct('LeaderBoardGoalControlAt', cmd_LeaderBoardGoalControlAt))
	actions.append(EUDCommandStruct('LeaderBoardGoalResources', cmd_LeaderBoardGoalResources))
	actions.append(EUDCommandStruct('LeaderBoardGoalKills', cmd_LeaderBoardGoalKills))
	actions.append(EUDCommandStruct('LeaderBoardGoalScore', cmd_LeaderBoardGoalScore))
	actions.append(EUDCommandStruct('MoveLocation', cmd_MoveLocation))
	actions.append(EUDCommandStruct('MoveUnit', cmd_MoveUnit))
	actions.append(EUDCommandStruct('LeaderBoardGreed', cmd_LeaderBoardGreed))
	actions.append(EUDCommandStruct('SetNextScenario', cmd_SetNextScenario))
	actions.append(EUDCommandStruct('SetDoodadState', cmd_SetDoodadState))
	actions.append(EUDCommandStruct('SetInvincibility', cmd_SetInvincibility))
	actions.append(EUDCommandStruct('CreateUnit', cmd_CreateUnit))
	actions.append(EUDCommandStruct('SetDeaths', cmd_SetDeaths))
	actions.append(EUDCommandStruct('Order', cmd_Order))
	actions.append(EUDCommandStruct('Comment', cmd_Comment))
	actions.append(EUDCommandStruct('GiveUnits', cmd_GiveUnits))
	actions.append(EUDCommandStruct('ModifyUnitHitPoints', cmd_ModifyUnitHitPoints))
	actions.append(EUDCommandStruct('ModifyUnitEnergy', cmd_ModifyUnitEnergy))
	actions.append(EUDCommandStruct('ModifyUnitShields', cmd_ModifyUnitShields))
	actions.append(EUDCommandStruct('ModifyUnitResourceAmount', cmd_ModifyUnitResourceAmount))
	actions.append(EUDCommandStruct('ModifyUnitHangarCount', cmd_ModifyUnitHangarCount))
	actions.append(EUDCommandStruct('PauseTimer', cmd_PauseTimer))
	actions.append(EUDCommandStruct('UnpauseTimer', cmd_UnpauseTimer))
	actions.append(EUDCommandStruct('Draw', cmd_Draw))
	actions.append(EUDCommandStruct('SetAllianceStatus', cmd_SetAllianceStatus))
	actions.append(EUDCommandStruct('SetMemory', cmd_SetMemory))
	actions.append(EUDCommandStruct('SetMemoryEPD', cmd_SetMemoryEPD))
	actions.append(EUDCommandStruct('SetDeathsX', cmd_SetDeathsX))
	actions.append(EUDCommandStruct('SetMemoryX', cmd_SetMemoryX))

	return actions

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

