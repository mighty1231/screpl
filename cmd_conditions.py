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
from decoder import retDecBool
from command import EUDCommand

def register_all_conditioncmds():
	from tables import RegisterCommand

	RegisterCommand('CountdownTimer', cmd_CountdownTimer)
	RegisterCommand('Command', cmd_Command)
	RegisterCommand('Bring', cmd_Bring)
	RegisterCommand('Accumulate', cmd_Accumulate)
	RegisterCommand('Kills', cmd_Kills)
	RegisterCommand('CommandMost', cmd_CommandMost)
	RegisterCommand('CommandMostAt', cmd_CommandMostAt)
	RegisterCommand('MostKills', cmd_MostKills)
	RegisterCommand('HighestScore', cmd_HighestScore)
	RegisterCommand('MostResources', cmd_MostResources)
	RegisterCommand('Switch', cmd_Switch)
	RegisterCommand('ElapsedTime', cmd_ElapsedTime)
	RegisterCommand('Opponents', cmd_Opponents)
	RegisterCommand('Deaths', cmd_Deaths)
	RegisterCommand('CommandLeast', cmd_CommandLeast)
	RegisterCommand('CommandLeastAt', cmd_CommandLeastAt)
	RegisterCommand('LeastKills', cmd_LeastKills)
	RegisterCommand('LowestScore', cmd_LowestScore)
	RegisterCommand('LeastResources', cmd_LeastResources)
	RegisterCommand('Score', cmd_Score)
	RegisterCommand('Always', cmd_Always)
	RegisterCommand('Never', cmd_Never)
	RegisterCommand('Memory', cmd_Memory)
	RegisterCommand('MemoryEPD', cmd_MemoryEPD)
	RegisterCommand('DeathsX', cmd_DeathsX)
	RegisterCommand('MemoryX', cmd_MemoryX)

@EUDCommand([argEncComparison, argEncNumber], [retDecBool])
def cmd_CountdownTimer(Comparison, Time):
	if EUDIf()(CountdownTimer(Comparison, Time)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([argEncPlayer, argEncComparison, argEncNumber, argEncUnit], [retDecBool])
def cmd_Command(Player, Comparison, Number, Unit):
	if EUDIf()(Command(Player, Comparison, Number, Unit)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([argEncPlayer, argEncComparison, argEncUnit, argEncNumber, argEncLocation], [retDecBool])
def cmd_Bring(Player, Comparison, Number, Unit, Location):
	if EUDIf()(Bring(Player, Comparison, Number, Unit, Location)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([argEncPlayer, argEncComparison, argEncNumber, argEncResource], [retDecBool])
def cmd_Accumulate(Player, Comparison, Number, ResourceType):
	if EUDIf()(Accumulate(Player, Comparison, Number, ResourceType)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([argEncPlayer, argEncComparison, argEncNumber, argEncUnit], [retDecBool])
def cmd_Kills(Player, Comparison, Number, Unit):
	if EUDIf()(Kills(Player, Comparison, Number, Unit)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([argEncUnit], [retDecBool])
def cmd_CommandMost(Unit):
	if EUDIf()(CommandMost(Unit)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([argEncUnit, argEncLocation], [retDecBool])
def cmd_CommandMostAt(Unit, Location):
	if EUDIf()(CommandMostAt(Unit, Location)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([argEncUnit], [retDecBool])
def cmd_MostKills(Unit):
	if EUDIf()(MostKills(Unit)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([argEncScore], [retDecBool])
def cmd_HighestScore(ScoreType):
	if EUDIf()(HighestScore(ScoreType)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([argEncResource], [retDecBool])
def cmd_MostResources(ResourceType):
	if EUDIf()(MostResources(ResourceType)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([argEncSwitch, argEncSwitchState], [retDecBool])
def cmd_Switch(switch, state):
	if EUDIf()(Switch(switch, state)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([argEncComparison, argEncNumber], [retDecBool])
def cmd_ElapsedTime(Comparison, Time):
	if EUDIf()(ElapsedTime(Comparison, Time)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([argEncPlayer, argEncComparison, argEncNumber], [retDecBool])
def cmd_Opponents(Player, Comparison, Number):
	if EUDIf()(Opponents(Player, Comparison, Number)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([argEncPlayer, argEncComparison, argEncNumber, argEncUnit], [retDecBool])
def cmd_Deaths(Player, Comparison, Number, Unit):
	if EUDIf()(Deaths(Player, Comparison, Number, Unit)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([argEncUnit], [retDecBool])
def cmd_CommandLeast(Unit):
	if EUDIf()(CommandLeast(Unit)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([argEncUnit, argEncLocation], [retDecBool])
def cmd_CommandLeastAt(Unit, Location):
	if EUDIf()(CommandLeastAt(Unit, Location)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([argEncUnit], [retDecBool])
def cmd_LeastKills(Unit):
	if EUDIf()(LeastKills(Unit)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([argEncScore], [retDecBool])
def cmd_LowestScore(ScoreType):
	if EUDIf()(LowestScore(ScoreType)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([argEncResource], [retDecBool])
def cmd_LeastResources(ResourceType):
	if EUDIf()(LeastResources(ResourceType)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([argEncPlayer, argEncScore, argEncComparison, argEncNumber], [retDecBool])
def cmd_Score(Player, ScoreType, Comparison, Number):
	if EUDIf()(Score(Player, ScoreType, Comparison, Number)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([], [retDecBool])
def cmd_Always():
	if EUDIf()(Always()):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([], [retDecBool])
def cmd_Never():
	if EUDIf()(Never()):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([argEncNumber, argEncComparison, argEncNumber], [retDecBool])
def cmd_Memory(dest, cmptype, value):
	if EUDIf()(Memory(dest, cmptype, value)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([argEncNumber, argEncComparison, argEncNumber], [retDecBool])
def cmd_MemoryEPD(dest, cmptype, value):
	if EUDIf()(MemoryEPD(dest, cmptype, value)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([argEncPlayer, argEncComparison, argEncNumber, argEncUnit, argEncNumber], [retDecBool])
def cmd_DeathsX(Player, Comparison, Number, Unit, Mask):
	if EUDIf()(DeathsX(Player, Comparison, Number, Unit, Mask)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDCommand([argEncNumber, argEncComparison, argEncNumber, argEncNumber], [retDecBool])
def cmd_MemoryX(dest, cmptype, value, mask):
	if EUDIf()(MemoryX(dest, cmptype, value, mask)):
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)
