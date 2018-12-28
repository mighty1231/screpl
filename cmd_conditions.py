from eudplib import *
from utils import *
from constenc import (
	arg_EncodeNumber,
	arg_EncodeCount,
	arg_EncodeModifier,
	arg_EncodeAllyStatus,
	arg_EncodeComparison,
	arg_EncodeOrder,
	arg_EncodePlayer,
	arg_EncodePropState,
	arg_EncodeResource,
	arg_EncodeScore,
	arg_EncodeSwitchAction,
	arg_EncodeSwitchState,
)
from strenc import (
	arg_EncodeUnit,
	arg_EncodeLocation,
	arg_EncodeAIScript,
	arg_EncodeSwitch,
	arg_EncodeString,
)
from decoder import ret_DecodeBool
from command import EUDCommand, EUDCommandStruct

def cmdstruct_all_conditions():
	conditions = []
	conditions.append(EUDCommandStruct('CountdownTimer', cmd_CountdownTimer))
	conditions.append(EUDCommandStruct('Command', cmd_Command))
	conditions.append(EUDCommandStruct('Bring', cmd_Bring))
	conditions.append(EUDCommandStruct('Accumulate', cmd_Accumulate))
	conditions.append(EUDCommandStruct('Kills', cmd_Kills))
	conditions.append(EUDCommandStruct('CommandMost', cmd_CommandMost))
	conditions.append(EUDCommandStruct('CommandMostAt', cmd_CommandMostAt))
	conditions.append(EUDCommandStruct('MostKills', cmd_MostKills))
	conditions.append(EUDCommandStruct('HighestScore', cmd_HighestScore))
	conditions.append(EUDCommandStruct('MostResources', cmd_MostResources))
	conditions.append(EUDCommandStruct('Switch', cmd_Switch))
	conditions.append(EUDCommandStruct('ElapsedTime', cmd_ElapsedTime))
	conditions.append(EUDCommandStruct('Opponents', cmd_Opponents))
	conditions.append(EUDCommandStruct('Deaths', cmd_Deaths))
	conditions.append(EUDCommandStruct('CommandLeast', cmd_CommandLeast))
	conditions.append(EUDCommandStruct('CommandLeastAt', cmd_CommandLeastAt))
	conditions.append(EUDCommandStruct('LeastKills', cmd_LeastKills))
	conditions.append(EUDCommandStruct('LowestScore', cmd_LowestScore))
	conditions.append(EUDCommandStruct('LeastResources', cmd_LeastResources))
	conditions.append(EUDCommandStruct('Score', cmd_Score))
	conditions.append(EUDCommandStruct('Always', cmd_Always))
	conditions.append(EUDCommandStruct('Never', cmd_Never))
	conditions.append(EUDCommandStruct('Memory', cmd_Memory))
	conditions.append(EUDCommandStruct('MemoryEPD', cmd_MemoryEPD))
	conditions.append(EUDCommandStruct('DeathsX', cmd_DeathsX))
	conditions.append(EUDCommandStruct('MemoryX', cmd_MemoryX))

	return conditions

@EUDCommand([arg_EncodeComparison, arg_EncodeNumber], [ret_DecodeBool])
def cmd_CountdownTimer(Comparison, Time):
	if EUDIf()(CountdownTimer(Comparison, Time)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([arg_EncodePlayer, arg_EncodeComparison, arg_EncodeNumber, arg_EncodeUnit], [ret_DecodeBool])
def cmd_Command(Player, Comparison, Number, Unit):
	if EUDIf()(Command(Player, Comparison, Number, Unit)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([arg_EncodePlayer, arg_EncodeComparison, arg_EncodeUnit, arg_EncodeNumber, arg_EncodeLocation], [ret_DecodeBool])
def cmd_Bring(Player, Comparison, Number, Unit, Location):
	if EUDIf()(Bring(Player, Comparison, Number, Unit, Location)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([arg_EncodePlayer, arg_EncodeComparison, arg_EncodeNumber, arg_EncodeResource], [ret_DecodeBool])
def cmd_Accumulate(Player, Comparison, Number, ResourceType):
	if EUDIf()(Accumulate(Player, Comparison, Number, ResourceType)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([arg_EncodePlayer, arg_EncodeComparison, arg_EncodeNumber, arg_EncodeUnit], [ret_DecodeBool])
def cmd_Kills(Player, Comparison, Number, Unit):
	if EUDIf()(Kills(Player, Comparison, Number, Unit)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([arg_EncodeUnit], [ret_DecodeBool])
def cmd_CommandMost(Unit):
	if EUDIf()(CommandMost(Unit)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([arg_EncodeUnit, arg_EncodeLocation], [ret_DecodeBool])
def cmd_CommandMostAt(Unit, Location):
	if EUDIf()(CommandMostAt(Unit, Location)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([arg_EncodeUnit], [ret_DecodeBool])
def cmd_MostKills(Unit):
	if EUDIf()(MostKills(Unit)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([arg_EncodeScore], [ret_DecodeBool])
def cmd_HighestScore(ScoreType):
	if EUDIf()(HighestScore(ScoreType)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([arg_EncodeResource], [ret_DecodeBool])
def cmd_MostResources(ResourceType):
	if EUDIf()(MostResources(ResourceType)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([arg_EncodeSwitch, arg_EncodeSwitchState], [ret_DecodeBool])
def cmd_Switch(switch, state):
	if EUDIf()(Switch(switch, state)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([arg_EncodeComparison, arg_EncodeNumber], [ret_DecodeBool])
def cmd_ElapsedTime(Comparison, Time):
	if EUDIf()(ElapsedTime(Comparison, Time)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([arg_EncodePlayer, arg_EncodeComparison, arg_EncodeNumber], [ret_DecodeBool])
def cmd_Opponents(Player, Comparison, Number):
	if EUDIf()(Opponents(Player, Comparison, Number)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([arg_EncodePlayer, arg_EncodeComparison, arg_EncodeNumber, arg_EncodeUnit], [ret_DecodeBool])
def cmd_Deaths(Player, Comparison, Number, Unit):
	if EUDIf()(Deaths(Player, Comparison, Number, Unit)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([arg_EncodeUnit], [ret_DecodeBool])
def cmd_CommandLeast(Unit):
	if EUDIf()(CommandLeast(Unit)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([arg_EncodeUnit, arg_EncodeLocation], [ret_DecodeBool])
def cmd_CommandLeastAt(Unit, Location):
	if EUDIf()(CommandLeastAt(Unit, Location)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([arg_EncodeUnit], [ret_DecodeBool])
def cmd_LeastKills(Unit):
	if EUDIf()(LeastKills(Unit)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([arg_EncodeScore], [ret_DecodeBool])
def cmd_LowestScore(ScoreType):
	if EUDIf()(LowestScore(ScoreType)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([arg_EncodeResource], [ret_DecodeBool])
def cmd_LeastResources(ResourceType):
	if EUDIf()(LeastResources(ResourceType)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([arg_EncodePlayer, arg_EncodeScore, arg_EncodeComparison, arg_EncodeNumber], [ret_DecodeBool])
def cmd_Score(Player, ScoreType, Comparison, Number):
	if EUDIf()(Score(Player, ScoreType, Comparison, Number)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([], [ret_DecodeBool])
def cmd_Always():
	if EUDIf()(Always()):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([], [ret_DecodeBool])
def cmd_Never():
	if EUDIf()(Never()):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([arg_EncodeNumber, arg_EncodeComparison, arg_EncodeNumber], [ret_DecodeBool])
def cmd_Memory(dest, cmptype, value):
	if EUDIf()(Memory(dest, cmptype, value)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([arg_EncodeNumber, arg_EncodeComparison, arg_EncodeNumber], [ret_DecodeBool])
def cmd_MemoryEPD(dest, cmptype, value):
	if EUDIf()(MemoryEPD(dest, cmptype, value)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([arg_EncodePlayer, arg_EncodeComparison, arg_EncodeNumber, arg_EncodeUnit, arg_EncodeNumber], [ret_DecodeBool])
def cmd_DeathsX(Player, Comparison, Number, Unit, Mask):
	if EUDIf()(eudx.DeathsX(Player, Comparison, Number, Unit, Mask)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([arg_EncodeNumber, arg_EncodeComparison, arg_EncodeNumber, arg_EncodeNumber], [ret_DecodeBool])
def cmd_MemoryX(dest, cmptype, value, mask):
	if EUDIf()(eudx.MemoryX(dest, cmptype, value, mask)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)
