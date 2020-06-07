from eudplib import *

from eudplib.core.mapdata.stringmap import swmap, locmap
from eudplib.core.rawtrigger.strdict import DefAIScriptDict

from screpl.utils.byterw import REPLByteRW
from screpl.utils.conststring import EPDConstString
from screpl.utils.debug import f_raise_error
from screpl.utils.referencetable import ReferenceTable

AIScript = ReferenceTable(
    list(map(lambda a: (a[0], b2i4(a[1])), DefAIScriptDict.items())),
    key_f=EPDConstString, sortkey_f=lambda k, v: k, final=True)
Modifier = ReferenceTable([
    ("SetTo", SetTo),
    ("Add", Add),
    ("Subtract", Subtract),
], key_f=EPDConstString, value_f=EncodeModifier, final=True)
AllyStatus = ReferenceTable([
    ("Enemy", Enemy),
    ("Ally", Ally),
    ("AlliedVictory", AlliedVictory),
], key_f=EPDConstString, value_f=EncodeAllyStatus, final=True)
Comparison = ReferenceTable([
    ("AtLeast", AtLeast),
    ("AtMost", AtMost),
    ("Exactly", Exactly),
], key_f=EPDConstString, value_f=EncodeComparison, final=True)
Order = ReferenceTable([
    ("Move", Move),
    ("Patrol", Patrol),
    ("Attack", Attack),
], key_f=EPDConstString, value_f=EncodeOrder, final=True)
Player = ReferenceTable([
    ("Player1", Player1),
    ("Player2", Player2),
    ("Player3", Player3),
    ("Player4", Player4),
    ("Player5", Player5),
    ("Player6", Player6),
    ("Player7", Player7),
    ("Player8", Player8),
    ("Player9", Player9),
    ("Player10", Player10),
    ("Player11", Player11),
    ("Player12", Player12),
    ("CurrentPlayer", CurrentPlayer),
    ("Foes", Foes),
    ("Allies", Allies),
    ("NeutralPlayers", NeutralPlayers),
    ("AllPlayers", AllPlayers),
    ("Force1", Force1),
    ("Force2", Force2),
    ("Force3", Force3),
    ("Force4", Force4),
    ("NonAlliedVictoryPlayers", NonAlliedVictoryPlayers),
], key_f=EPDConstString, value_f=EncodePlayer, final=True)
PropState = ReferenceTable([
    ("Enable", Enable),
    ("Disable", Disable),
    ("Toggle", Toggle),
], key_f=EPDConstString, value_f=EncodePropState, final=True)
Resource = ReferenceTable([
    ("Ore", Ore),
    ("Gas", Gas),
    ("OreAndGas", OreAndGas),
], key_f=EPDConstString, value_f=EncodeResource, final=True)
Score = ReferenceTable([
    ("Total", Total),
    ("Units", Units),
    ("Buildings", Buildings),
    ("UnitsAndBuildings", UnitsAndBuildings),
    ("Kills", Kills),
    ("Razings", Razings),
    ("KillsAndRazings", KillsAndRazings),
    ("Custom", Custom),
], key_f=EPDConstString, value_f=EncodeScore, final=True)
SwitchAction = ReferenceTable([
    ("Set", Set),
    ("Clear", Clear),
    ("Toggle", Toggle),
    ("Random", Random),
], key_f=EPDConstString, value_f=EncodeSwitchAction, final=True)
SwitchState = ReferenceTable([
    ("Set", Set),
    ("Cleared", Cleared),
], key_f=EPDConstString, value_f=EncodeSwitchState, final=True)
Count = ReferenceTable(
    [("All", All)]
    + [(str(d), d) for d in range(1, 256)]
, key_f=EPDConstString, value_f=EncodeCount, final=True)

# location and switch
NAME_SIZE = 100
_locationnames = bytearray(NAME_SIZE*255)
for k, v in locmap._s2id.items():
    length = len(k)
    _locationnames[NAME_SIZE*v:NAME_SIZE*v+length] = k
_locationname_db_epd = EPD(Db(_locationnames))

def get_locationname_epd(location_idx):
    if EUDIfNot()([1 <= location_idx, location_idx <= 255]):
        f_raise_error("get_locationname_epd: IndexError")
    EUDEndIf()
    return (_locationname_db_epd - (NAME_SIZE//4)
            + location_idx * (NAME_SIZE//4))

_switchnames = bytearray(NAME_SIZE*256)
for k, v in swmap._s2id.items():
    length = len(k)
    _switchnames[NAME_SIZE*v:NAME_SIZE*v+length] = k
_switchname_db_epd = EPD(Db(_switchnames))

def get_switchname_epd(switch_idx):
    if EUDIfNot()(switch_idx <= 255):
        f_raise_error("get_switchname_epd: IndexError")
    EUDEndIf()
    return (_switchname_db_epd - (NAME_SIZE//4)
            + switch_idx * (NAME_SIZE//4))

_arr_defaultunitnames = EUDArray(list(map(EPDConstString, [
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

def get_default_unitname_epd(unitid):
    return _arr_defaultunitnames[unitid]
