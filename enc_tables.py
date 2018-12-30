from eudplib import *
from table import ReferenceTable, SearchTable
from utils import *
from eudplib.core.rawtrigger.strdict import (
    DefUnitDict,
    DefAIScriptDict,
    DefLocationDict,
    DefSwitchDict,
)
from eudplib.core.mapdata.stringmap import (
    unitmap,
    locmap,
    swmap
)
from command import EUDCommand
from encoder import ReadName

encodingTables = ReferenceTable(key_f=makeEPDText, value_f=EPD)

# string encoders
tb_unit = ReferenceTable(DefUnitDict.items(), [(encodingTables, "Unit")], key_f=makeEPDText)
tb_locSub = ReferenceTable(DefLocationDict.items(), [(encodingTables, "LocationSub")], key_f=makeEPDText)
tb_swSub = ReferenceTable(DefSwitchDict.items(), [(encodingTables, "SwitchSub")], key_f=makeEPDText)
tb_ai = ReferenceTable(
        list(map(lambda a:(a[0], b2i4(a[1])), DefAIScriptDict.items())),
        [(encodingTables, "AIScript")], key_f=makeEPDText)

tb_unitMap = ReferenceTable(unitmap._s2id.items(), [(encodingTables, "Unit")], key_f=makeEPDText)
tb_locMap = ReferenceTable(
    list(map(lambda a:(a[0], a[1]+1), locmap._s2id.items())), [(encodingTables, "Location")], key_f=makeEPDText)
tb_swMap = ReferenceTable(swmap._s2id.items(), [(encodingTables, "Switch")], key_f=makeEPDText)

tb_Modifier = ReferenceTable([
    ("SetTo", EncodeModifier(SetTo)),
    ("Add", EncodeModifier(Add)),
    ("Subtract", EncodeModifier(Subtract)),
], [(encodingTables, "Modifier")], key_f=makeEPDText)
tb_AllyStatus = ReferenceTable([
    ("Enemy", EncodeAllyStatus(Enemy)),
    ("Ally", EncodeAllyStatus(Ally)),
    ("AlliedVictory", EncodeAllyStatus(AlliedVictory)),
], [(encodingTables, "AllyStatus")], key_f=makeEPDText)
tb_Comparison = ReferenceTable([
    ("AtLeast", EncodeComparison(AtLeast)),
    ("AtMost", EncodeComparison(AtMost)),
    ("Exactly", EncodeComparison(Exactly)),
], [(encodingTables, "Comparison")], key_f=makeEPDText)
tb_Order = ReferenceTable([
    ("Move", EncodeOrder(Move)),
    ("Patrol", EncodeOrder(Patrol)),
    ("Attack", EncodeOrder(Attack)),
], [(encodingTables, "Order")], key_f=makeEPDText)
tb_Player = ReferenceTable([
    ("P1", EncodePlayer(P1)),
    ("P2", EncodePlayer(P2)),
    ("P3", EncodePlayer(P3)),
    ("P4", EncodePlayer(P4)),
    ("P5", EncodePlayer(P5)),
    ("P6", EncodePlayer(P6)),
    ("P7", EncodePlayer(P7)),
    ("P8", EncodePlayer(P8)),
    ("P9", EncodePlayer(P9)),
    ("P10", EncodePlayer(P10)),
    ("P11", EncodePlayer(P11)),
    ("P12", EncodePlayer(P12)),
    ("Player1", EncodePlayer(Player1)),
    ("Player2", EncodePlayer(Player2)),
    ("Player3", EncodePlayer(Player3)),
    ("Player4", EncodePlayer(Player4)),
    ("Player5", EncodePlayer(Player5)),
    ("Player6", EncodePlayer(Player6)),
    ("Player7", EncodePlayer(Player7)),
    ("Player8", EncodePlayer(Player8)),
    ("Player9", EncodePlayer(Player9)),
    ("Player10", EncodePlayer(Player10)),
    ("Player11", EncodePlayer(Player11)),
    ("Player12", EncodePlayer(Player12)),
    ("CurrentPlayer", EncodePlayer(CurrentPlayer)),
    ("Foes", EncodePlayer(Foes)),
    ("Allies", EncodePlayer(Allies)),
    ("NeutralPlayers", EncodePlayer(NeutralPlayers)),
    ("AllPlayers", EncodePlayer(AllPlayers)),
    ("Force1", EncodePlayer(Force1)),
    ("Force2", EncodePlayer(Force2)),
    ("Force3", EncodePlayer(Force3)),
    ("Force4", EncodePlayer(Force4)),
    ("NonAlliedVictoryPlayers", EncodePlayer(NonAlliedVictoryPlayers)),
], [(encodingTables, "Player")], key_f=makeEPDText)
tb_PropState = ReferenceTable([
    ("Enable", EncodePropState(Enable)),
    ("Disable", EncodePropState(Disable)),
    ("Toggle", EncodePropState(Toggle)),
], [(encodingTables, "PropState")], key_f=makeEPDText)
tb_Resource = ReferenceTable([
    ("Ore", EncodeResource(Ore)),
    ("Gas", EncodeResource(Gas)),
    ("OreAndGas", EncodeResource(OreAndGas)),
], [(encodingTables, "Resource")], key_f=makeEPDText)
tb_Score = ReferenceTable([
    ("Total", EncodeScore(Total)),
    ("Units", EncodeScore(Units)),
    ("Buildings", EncodeScore(Buildings)),
    ("UnitsAndBuildings", EncodeScore(UnitsAndBuildings)),
    ("Kills", EncodeScore(Kills)),
    ("Razings", EncodeScore(Razings)),
    ("KillsAndRazings", EncodeScore(KillsAndRazings)),
    ("Custom", EncodeScore(Custom)),
], [(encodingTables, "Score")], key_f=makeEPDText)
tb_SwitchAction = ReferenceTable([
    ("Set", EncodeSwitchAction(Set)),
    ("Clear", EncodeSwitchAction(Clear)),
    ("Toggle", EncodeSwitchAction(Toggle)),
    ("Random", EncodeSwitchAction(Random)),
], [(encodingTables, "SwitchAction")], key_f=makeEPDText)
tb_SwitchState = ReferenceTable([
    ("Set", EncodeSwitchState(Set)),
    ("Cleared", EncodeSwitchState(Cleared)),
], [(encodingTables, "SwitchState")], key_f=makeEPDText)

@EUDCommand([])
def cmd_listEncoders():
	from board import Board
	br = Board.GetInstance()
	br.SetTitle(makeText('List of encoders'))
	br.SetContentWithTbName_epd(EPD(encodingTables))
	br.SetMode(1)

@EUDFunc
def argEncEncoderName(offset, delim, ref_offset_epd, retval_epd):
	tmpbuf = Db(150)
	if EUDIf()(ReadName(offset, delim, ref_offset_epd, EPD(tmpbuf)) == 1):
		if EUDIf()(SearchTable(tmpbuf, EPD(encodingTables), f_strcmp_ptrepd, retval_epd) == 1):
			EUDReturn(1)
		EUDEndIf()
	EUDEndIf()
	f_dwwrite_epd(ref_offset_epd, offset)
	EUDReturn(0)

@EUDCommand([argEncEncoderName])
def cmd_printEncoder(table_epd):
	from board import Board
	br = Board.GetInstance()
	br.SetTitle(makeText('List'))
	br.SetContentWithTbName_epd(table_epd)
	br.SetMode(1)

def register_encoder():
	from repl import RegisterCommand
	RegisterCommand("tables", cmd_listEncoders)
	RegisterCommand("contents", cmd_printEncoder)
