from eudplib import *
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
from ...base.referencetable import ReferenceTable
from ...utils import EPDConstString

tb_unit = ReferenceTable(
    DefUnitDict.items(),
    key_f=EPDConstString, sortkey_f=lambda k,v:k)
tb_locSub = ReferenceTable(
    DefLocationDict.items(),
    key_f=EPDConstString, sortkey_f=lambda k,v:k)
tb_swSub = ReferenceTable(
    DefSwitchDict.items(),
    key_f=EPDConstString, sortkey_f=lambda k,v:k)
tb_ai = ReferenceTable(
    list(map(lambda a:(a[0], b2i4(a[1])), DefAIScriptDict.items())),
    key_f=EPDConstString, sortkey_f=lambda k,v:k)

tb_unitMap = ReferenceTable(
    unitmap._s2id.items(),
    key_f=EPDConstString, sortkey_f=lambda k,v:k)
tb_locMap = ReferenceTable(
    list(map(lambda a:(a[0], a[1]+1), locmap._s2id.items())),
    key_f=EPDConstString, sortkey_f=lambda k,v:k)
tb_swMap = ReferenceTable(
    swmap._s2id.items(),
    key_f=EPDConstString, sortkey_f=lambda k,v:k)

tb_Modifier = ReferenceTable([
    ("SetTo", EncodeModifier(SetTo)),
    ("Add", EncodeModifier(Add)),
    ("Subtract", EncodeModifier(Subtract)),
], key_f=EPDConstString)
tb_AllyStatus = ReferenceTable([
    ("Enemy", EncodeAllyStatus(Enemy)),
    ("Ally", EncodeAllyStatus(Ally)),
    ("AlliedVictory", EncodeAllyStatus(AlliedVictory)),
], key_f=EPDConstString)
tb_Comparison = ReferenceTable([
    ("AtLeast", EncodeComparison(AtLeast)),
    ("AtMost", EncodeComparison(AtMost)),
    ("Exactly", EncodeComparison(Exactly)),
], key_f=EPDConstString)
tb_Order = ReferenceTable([
    ("Move", EncodeOrder(Move)),
    ("Patrol", EncodeOrder(Patrol)),
    ("Attack", EncodeOrder(Attack)),
], key_f=EPDConstString)
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
], key_f=EPDConstString)
tb_PropState = ReferenceTable([
    ("Enable", EncodePropState(Enable)),
    ("Disable", EncodePropState(Disable)),
    ("Toggle", EncodePropState(Toggle)),
], key_f=EPDConstString)
tb_Resource = ReferenceTable([
    ("Ore", EncodeResource(Ore)),
    ("Gas", EncodeResource(Gas)),
    ("OreAndGas", EncodeResource(OreAndGas)),
], key_f=EPDConstString)
tb_Score = ReferenceTable([
    ("Total", EncodeScore(Total)),
    ("Units", EncodeScore(Units)),
    ("Buildings", EncodeScore(Buildings)),
    ("UnitsAndBuildings", EncodeScore(UnitsAndBuildings)),
    ("Kills", EncodeScore(Kills)),
    ("Razings", EncodeScore(Razings)),
    ("KillsAndRazings", EncodeScore(KillsAndRazings)),
    ("Custom", EncodeScore(Custom)),
], key_f=EPDConstString)
tb_SwitchAction = ReferenceTable([
    ("Set", EncodeSwitchAction(Set)),
    ("Clear", EncodeSwitchAction(Clear)),
    ("Toggle", EncodeSwitchAction(Toggle)),
    ("Random", EncodeSwitchAction(Random)),
], key_f=EPDConstString)
tb_SwitchState = ReferenceTable([
    ("Set", EncodeSwitchState(Set)),
    ("Cleared", EncodeSwitchState(Cleared)),
], key_f=EPDConstString)

