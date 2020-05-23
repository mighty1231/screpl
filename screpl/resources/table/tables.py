from eudplib import *

from eudplib.core.rawtrigger.strdict import (
    DefAIScriptDict,
    DefSwitchDict,
)
from eudplib.core.mapdata.stringmap import swmap, locmap

from screpl.utils.conststring import EPDConstString
from screpl.utils.debug import f_raise_error
from screpl.utils.eudbyterw import EUDByteRW
from screpl.utils.referencetable import ReferenceTable

swSub = ReferenceTable(
    DefSwitchDict.items(),
    key_f=EPDConstString, sortkey_f=lambda k,v:k)
swMap = ReferenceTable(
    swmap._s2id.items(),
    key_f=EPDConstString, sortkey_f=lambda k,v:k)
AIScript = ReferenceTable(
    list(map(lambda a:(a[0], b2i4(a[1])), DefAIScriptDict.items())),
    key_f=EPDConstString, sortkey_f=lambda k,v:k)
Modifier = ReferenceTable([
    ("SetTo", EncodeModifier(SetTo)),
    ("Add", EncodeModifier(Add)),
    ("Subtract", EncodeModifier(Subtract)),
], key_f=EPDConstString)
AllyStatus = ReferenceTable([
    ("Enemy", EncodeAllyStatus(Enemy)),
    ("Ally", EncodeAllyStatus(Ally)),
    ("AlliedVictory", EncodeAllyStatus(AlliedVictory)),
], key_f=EPDConstString)
Comparison = ReferenceTable([
    ("AtLeast", EncodeComparison(AtLeast)),
    ("AtMost", EncodeComparison(AtMost)),
    ("Exactly", EncodeComparison(Exactly)),
], key_f=EPDConstString)
Order = ReferenceTable([
    ("Move", EncodeOrder(Move)),
    ("Patrol", EncodeOrder(Patrol)),
    ("Attack", EncodeOrder(Attack)),
], key_f=EPDConstString)
Player = ReferenceTable([
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
PropState = ReferenceTable([
    ("Enable", EncodePropState(Enable)),
    ("Disable", EncodePropState(Disable)),
    ("Toggle", EncodePropState(Toggle)),
], key_f=EPDConstString)
Resource = ReferenceTable([
    ("Ore", EncodeResource(Ore)),
    ("Gas", EncodeResource(Gas)),
    ("OreAndGas", EncodeResource(OreAndGas)),
], key_f=EPDConstString)
Score = ReferenceTable([
    ("Total", EncodeScore(Total)),
    ("Units", EncodeScore(Units)),
    ("Buildings", EncodeScore(Buildings)),
    ("UnitsAndBuildings", EncodeScore(UnitsAndBuildings)),
    ("Kills", EncodeScore(Kills)),
    ("Razings", EncodeScore(Razings)),
    ("KillsAndRazings", EncodeScore(KillsAndRazings)),
    ("Custom", EncodeScore(Custom)),
], key_f=EPDConstString)
SwitchAction = ReferenceTable([
    ("Set", EncodeSwitchAction(Set)),
    ("Clear", EncodeSwitchAction(Clear)),
    ("Toggle", EncodeSwitchAction(Toggle)),
    ("Random", EncodeSwitchAction(Random)),
], key_f=EPDConstString)
SwitchState = ReferenceTable([
    ("Set", EncodeSwitchState(Set)),
    ("Cleared", EncodeSwitchState(Cleared)),
], key_f=EPDConstString)

_locstrings = [bytes(100) for _ in range(255)]
for k, v in locmap._s2id.items():
    _locstrings[v] = k + bytes(100-len(k))
Location = ReferenceTable(
    list(map(lambda i:(EPD(Db(_locstrings[i])), i+1), range(255))))

def GetLocationNameEPDPointer(location_idx):
    return f_dwread_epd((EPD(Location) - 1) + location_idx * 2)

@EUDFunc
def SetLocationName(location_idx, new_string_offset):
    if EUDIfNot()([location_idx.AtLeast(1), location_idx.AtMost(255)]):
        f_raise_error("SC-REPL indexError on SetLocationName")
    EUDEndIf()
    writer = EUDByteRW()
    writer.seekepd(GetLocationNameEPDPointer(location_idx))
    writer.write_str(new_string_offset)
    writer.write(0)

arr_DefaultUnit = EUDArray(list(map(EPDConstString, [
    "Terran Marine",
    "Terran Ghost",
    "Terran Vulture",
    "Terran Goliath",
    "Goliath Turret",
    "Terran Siege Tank (Tank Mode)",
    "Siege Tank Turret (Tank Mode)",
    "Terran SCV",
    "Terran Wraith",
    "Terran Science Vessel",
    "Gui Montag (Firebat)",
    "Terran Dropship",
    "Terran Battlecruiser",
    "Spider Mine",
    "Nuclear Missile",
    "Terran Civilian",
    "Sarah Kerrigan (Ghost)",
    "Alan Schezar (Goliath)",
    "Alan Schezar Turret",
    "Jim Raynor (Vulture)",
    "Jim Raynor (Marine)",
    "Tom Kazansky (Wraith)",
    "Magellan (Science Vessel)",
    "Edmund Duke (Tank Mode)",
    "Edmund Duke Turret (Tank Mode)",
    "Edmund Duke (Siege Mode)",
    "Edmund Duke Turret (Siege Mode)",
    "Arcturus Mengsk (Battlecruiser)",
    "Hyperion (Battlecruiser)",
    "Norad II (Battlecruiser)",
    "Terran Siege Tank (Siege Mode)",
    "Siege Tank Turret (Siege Mode)",
    "Terran Firebat",
    "Scanner Sweep",
    "Terran Medic",
    "Zerg Larva",
    "Zerg Egg",
    "Zerg Zergling",
    "Zerg Hydralisk",
    "Zerg Ultralisk",
    "Zerg Broodling",
    "Zerg Drone",
    "Zerg Overlord",
    "Zerg Mutalisk",
    "Zerg Guardian",
    "Zerg Queen",
    "Zerg Defiler",
    "Zerg Scourge",
    "Torrasque (Ultralisk)",
    "Matriarch (Queen)",
    "Infested Terran",
    "Infested Kerrigan (Infested Terran)",
    "Unclean One (Defiler)",
    "Hunter Killer (Hydralisk)",
    "Devouring One (Zergling)",
    "Kukulza (Mutalisk)",
    "Kukulza (Guardian)",
    "Yggdrasill (Overlord)",
    "Terran Valkyrie",
    "Mutalisk Cocoon",
    "Protoss Corsair",
    "Protoss Dark Templar (Unit)",
    "Zerg Devourer",
    "Protoss Dark Archon",
    "Protoss Probe",
    "Protoss Zealot",
    "Protoss Dragoon",
    "Protoss High Templar",
    "Protoss Archon",
    "Protoss Shuttle",
    "Protoss Scout",
    "Protoss Arbiter",
    "Protoss Carrier",
    "Protoss Interceptor",
    "Protoss Dark Templar (Hero)",
    "Zeratul (Dark Templar)",
    "Tassadar/Zeratul (Archon)",
    "Fenix (Zealot)",
    "Fenix (Dragoon)",
    "Tassadar (Templar)",
    "Mojo (Scout)",
    "Warbringer (Reaver)",
    "Gantrithor (Carrier)",
    "Protoss Reaver",
    "Protoss Observer",
    "Protoss Scarab",
    "Danimoth (Arbiter)",
    "Aldaris (Templar)",
    "Artanis (Scout)",
    "Rhynadon (Badlands Critter)",
    "Bengalaas (Jungle Critter)",
    "Cargo Ship (Unused)",
    "Mercenary Gunship (Unused)",
    "Scantid (Desert Critter)",
    "Kakaru (Twilight Critter)",
    "Ragnasaur (Ashworld Critter)",
    "Ursadon (Ice World Critter)",
    "Lurker Egg",
    "Raszagal (Corsair)",
    "Samir Duran (Ghost)",
    "Alexei Stukov (Ghost)",
    "Map Revealer",
    "Gerard DuGalle (BattleCruiser)",
    "Zerg Lurker",
    "Infested Duran (Infested Terran)",
    "Disruption Web",
    "Terran Command Center",
    "Terran Comsat Station",
    "Terran Nuclear Silo",
    "Terran Supply Depot",
    "Terran Refinery",
    "Terran Barracks",
    "Terran Academy",
    "Terran Factory",
    "Terran Starport",
    "Terran Control Tower",
    "Terran Science Facility",
    "Terran Covert Ops",
    "Terran Physics Lab",
    "Starbase (Unused)",
    "Terran Machine Shop",
    "Repair Bay (Unused)",
    "Terran Engineering Bay",
    "Terran Armory",
    "Terran Missile Turret",
    "Terran Bunker",
    "Norad II (Crashed)",
    "Ion Cannon",
    "Uraj Crystal",
    "Khalis Crystal",
    "Infested Command Center",
    "Zerg Hatchery",
    "Zerg Lair",
    "Zerg Hive",
    "Zerg Nydus Canal",
    "Zerg Hydralisk Den",
    "Zerg Defiler Mound",
    "Zerg Greater Spire",
    "Zerg Queen's Nest",
    "Zerg Evolution Chamber",
    "Zerg Ultralisk Cavern",
    "Zerg Spire",
    "Zerg Spawning Pool",
    "Zerg Creep Colony",
    "Zerg Spore Colony",
    "Unused Zerg Building1",
    "Zerg Sunken Colony",
    "Zerg Overmind (With Shell)",
    "Zerg Overmind",
    "Zerg Extractor",
    "Mature Chrysalis",
    "Zerg Cerebrate",
    "Zerg Cerebrate Daggoth",
    "Unused Zerg Building2",
    "Protoss Nexus",
    "Protoss Robotics Facility",
    "Protoss Pylon",
    "Protoss Assimilator",
    "Unused Protoss Building1",
    "Protoss Observatory",
    "Protoss Gateway",
    "Unused Protoss Building2",
    "Protoss Photon Cannon",
    "Protoss Citadel of Adun",
    "Protoss Cybernetics Core",
    "Protoss Templar Archives",
    "Protoss Forge",
    "Protoss Stargate",
    "Stasis Cell/Prison",
    "Protoss Fleet Beacon",
    "Protoss Arbiter Tribunal",
    "Protoss Robotics Support Bay",
    "Protoss Shield Battery",
    "Khaydarin Crystal Formation",
    "Protoss Temple",
    "Xel'Naga Temple",
    "Mineral Field (Type 1)",
    "Mineral Field (Type 2)",
    "Mineral Field (Type 3)",
    "Cave (Unused)",
    "Cave-in (Unused)",
    "Cantina (Unused)",
    "Mining Platform (Unused)",
    "Independent Command Center (Unused)",
    "Independent Starport (Unused)",
    "Independent Jump Gate (Unused)",
    "Ruins (Unused)",
    "Khaydarin Crystal Formation (Unused)",
    "Vespene Geyser",
    "Warp Gate",
    "Psi Disrupter",
    "Zerg Marker",
    "Terran Marker",
    "Protoss Marker",
    "Zerg Beacon",
    "Terran Beacon",
    "Protoss Beacon",
    "Zerg Flag Beacon",
    "Terran Flag Beacon",
    "Protoss Flag Beacon",
    "Power Generator",
    "Overmind Cocoon",
    "Dark Swarm",
    "Floor Missile Trap",
    "Floor Hatch (Unused)",
    "Left Upper Level Door",
    "Right Upper Level Door",
    "Left Pit Door",
    "Right Pit Door",
    "Floor Gun Trap",
    "Left Wall Missile Trap",
    "Left Wall Flame Trap",
    "Right Wall Missile Trap",
    "Right Wall Flame Trap",
    "Start Location",
    "Flag",
    "Young Chrysalis",
    "Psi Emitter",
    "Data Disc",
    "Khaydarin Crystal",
    "Mineral Cluster Type 1",
    "Mineral Cluster Type 2",
    "Protoss Vespene Gas Orb Type 1",
    "Protoss Vespene Gas Orb Type 2",
    "Zerg Vespene Gas Sac Type 1",
    "Zerg Vespene Gas Sac Type 2",
    "Terran Vespene Gas Tank Type 1",
    "Terran Vespene Gas Tank Type 2",
    "(none)",
    "(any unit)",
    "(men)",
    "(buildings)",
    "(factories)"
])))

def GetDefaultUnitNameEPDPointer(unitid):
    return arr_DefaultUnit[unitid]
