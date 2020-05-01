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
from ...base.eudbyterw import EUDByteRW
from ...utils import EPDConstString, f_raiseError

tb_unit = ReferenceTable(
    DefUnitDict.items(),
    key_f=EPDConstString, sortkey_f=lambda k,v:k)
tb_locSub = ReferenceTable(
    DefLocationDict.items(),
    key_f=EPDConstString, sortkey_f=lambda k,v:k)
tb_swSub = ReferenceTable(
    DefSwitchDict.items(),
    key_f=EPDConstString, sortkey_f=lambda k,v:k)
tb_unitMap = ReferenceTable(
    unitmap._s2id.items(),
    key_f=EPDConstString, sortkey_f=lambda k,v:k)

# location string is modifiable
location_strings = [bytes(100) for _ in range(255)]
for k, v in locmap._s2id.items():
    location_strings[v] = k + bytes(100-len(k))
tb_locMap = ReferenceTable(
    list(map(lambda i:(EPD(Db(location_strings[i])), i+1), range(255))))

def getLocationNameEPDPointer(location_idx):
    return f_dwread_epd((EPD(tb_locMap) - 1) + location_idx * 2)

@EUDFunc
def changeLocationName(location_idx, new_string_offset):
    if EUDIfNot()([location_idx.AtLeast(1), location_idx.AtMost(255)]):
        f_raiseError("SC-REPL indexError on changeLocationName")
    EUDEndIf()
    writer = EUDByteRW()
    writer.seekepd(getLocationNameEPDPointer(location_idx))
    writer.write_str(new_string_offset)
    writer.write(0)

tb_swMap = ReferenceTable(
    swmap._s2id.items(),
    key_f=EPDConstString, sortkey_f=lambda k,v:k)

tb_AIScript = ReferenceTable(
    list(map(lambda a:(a[0], b2i4(a[1])), DefAIScriptDict.items())),
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

