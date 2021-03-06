from eudplib import *

from eudplib.core.mapdata.stringmap import swmap, locmap
from eudplib.core.rawtrigger.strdict import DefAIScriptDict

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
    + [(str(d), d) for d in range(1, 256)],
    key_f=EPDConstString, value_f=EncodeCount, final=True)

# location and switch
NAME_SIZE = 100
_locationnames = bytearray(NAME_SIZE*255)
for k, v in locmap._s2id.items():
    length = len(k)
    _locationnames[NAME_SIZE*v:NAME_SIZE*v+length] = k
for idx in range(255):
    if _locationnames[NAME_SIZE*idx] == 0:
        # SCMD-syntax
        default_name = "Location {}".format(idx+1)
        length = len(default_name)
        _locationnames[NAME_SIZE*idx:NAME_SIZE*idx+length] = default_name.encode()

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
for idx in range(256):
    if _switchnames[NAME_SIZE*idx] == 0:
        # SCMD-syntax
        default_name = "Switch{}".format(idx+1)
        length = len(default_name)
        _switchnames[NAME_SIZE*idx:NAME_SIZE*idx+length] = default_name.encode()
_switchname_db_epd = EPD(Db(_switchnames))

def get_switchname_epd(switch_idx):
    if EUDIfNot()(switch_idx <= 255):
        f_raise_error("get_switchname_epd: IndexError")
    EUDEndIf()
    return _switchname_db_epd + switch_idx * (NAME_SIZE//4)

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

ConditionType = ReferenceTable([
    ("CountdownTimer", 1),
    ("Command", 2),
    ("Bring", 3),
    ("Accumulate", 4),
    ("Kills", 5),
    ("CommandMost", 6),
    ("CommandMostAt", 7),
    ("MostKills", 8),
    ("HighestScore", 9),
    ("MostResources", 10),
    ("Switch", 11),
    ("ElapsedTime", 12),
    # ("Briefing", 13),
    ("Opponents", 14),
    ("Deaths", 15),
    ("CommandLeast", 16),
    ("CommandLeastAt", 17),
    ("LeastKills", 18),
    ("LowestScore", 19),
    ("LeastResources", 20),
    ("Score", 21),
    ("Always", 22),
    ("Never", 23),
], key_f=EPDConstString, final=True)

ActionType = ReferenceTable([
    ("Victory", 1),
    ("Defeat", 2),
    ("PreserveTrigger", 3),
    ("Wait", 4),
    ("PauseGame", 5),
    ("UnpauseGame", 6),
    ("Transmission", 7),
    ("PlayWAV", 8),
    ("DisplayText", 9),
    ("CenterView", 10),
    ("CreateUnitWithProperties", 11),
    ("SetMissionObjectives", 12),
    ("SetSwitch", 13),
    ("SetCountdownTimer", 14),
    ("RunAIScript", 15),
    ("RunAIScriptAt", 16),
    ("LeaderBoardControl", 17),
    ("LeaderBoardControlAt", 18),
    ("LeaderBoardResources", 19),
    ("LeaderBoardKills", 20),
    ("LeaderBoardScore", 21),
    ("KillUnit", 22),
    ("KillUnitAt", 23),
    ("RemoveUnit", 24),
    ("RemoveUnitAt", 25),
    ("SetResources", 26),
    ("SetScore", 27),
    ("MinimapPing", 28),
    ("TalkingPortrait", 29),
    ("MuteUnitSpeech", 30),
    ("UnMuteUnitSpeech", 31),
    ("LeaderBoardComputerPlayers", 32),
    ("LeaderBoardGoalControl", 33),
    ("LeaderBoardGoalControlAt", 34),
    ("LeaderBoardGoalResources", 35),
    ("LeaderBoardGoalKills", 36),
    ("LeaderBoardGoalScore", 37),
    ("MoveLocation", 38),
    ("MoveUnit", 39),
    ("LeaderBoardGreed", 40),
    ("SetNextScenario", 41),
    ("SetDoodadState", 42),
    ("SetInvincibility", 43),
    ("CreateUnit", 44),
    ("SetDeaths", 45),
    ("Order", 46),
    ("Comment", 47),
    ("GiveUnits", 48),
    ("ModifyUnitHitPoints", 49),
    ("ModifyUnitEnergy", 50),
    ("ModifyUnitShields", 51),
    ("ModifyUnitResourceAmount", 52),
    ("ModifyUnitHangarCount", 53),
    ("PauseTimer", 54),
    ("UnpauseTimer", 55),
    ("Draw", 56),
    ("SetAllianceStatus", 57),
], key_f=EPDConstString, final=True)

class _PropTable(ReferenceTable):
    """Property reference table

    Property Structure

     ======  ============= ========  ===========
     Offset  Field Name    Position  EPD Player
     ======  ============= ========  ===========
       +00   sprpvalid     dword0    EPD(prop)+0
       +02   prpvalid
       +04   player        dword1    EPD(prop)+1
       +05   hitpoint
       +06   shield
       +07   energy
       +08   resource      dword2    EPD(prop)+2
       +0C   hanger        dword3    EPD(prop)+3
       +0E   sprpflag
       +10   unused        dword4    EPD(prop)+4
     ======  ============= ========  ===========

    - hitpoint : 0~100(%)
    - shield   : 0~100(%)
    - energy   : 0~100(%)
    - resource : 0~4294967295
    - hanger   : 0~65536

    Special properties : True(Enabled)/False(Disabled)/None(Don't care)

    - clocked      : Unit is clocked.
    - burrowed     : Unit is burrowed.
    - intransit    : Unit is lifted. (In transit)
    - hallucinated : Unit is hallucination.
    - invincible   : Unit is invincible.

    UPRP may saved into 0x596cd8..? SC:R does not support the address

    reference:
    https://github.com/bwapi/bwapi/blob/master/Release_Binary/Starcraft/bwapi-data/data/Broodwar.map#L3165
    """

    COLOR_HITPOINT = '\x08'
    COLOR_SHIELD = '\x0E'
    COLOR_ENERGY = '\x0F'
    COLOR_RESOURCE = '\x17'
    COLOR_HANGER = '\x18'

    @staticmethod
    def decode_property(property_):
        assert isinstance(property_, bytes) and len(property_) == 20

        sprpvalid = b2i2(property_, 0x00)
        prpvalid = b2i2(property_, 0x02)
        hitpoint = b2i1(property_, 0x05)
        shield = b2i1(property_, 0x06)
        energy = b2i1(property_, 0x07)
        resource = b2i4(property_, 0x08)
        hanger = b2i2(property_, 0x0C)
        sprpflag = b2i2(property_, 0x0E)

        list_ = []
        for bit, color, value in [
                (1 << 1, _PropTable.COLOR_HITPOINT, hitpoint),
                (1 << 2, _PropTable.COLOR_SHIELD, shield),
                (1 << 3, _PropTable.COLOR_ENERGY, energy),
                (1 << 4, _PropTable.COLOR_RESOURCE, resource),
                (1 << 5, _PropTable.COLOR_HANGER, hanger)]:
            if prpvalid & bit:
                list_.append("{}{}".format(color, value))

        for bit, name in [(1 << 0, 'cloaked'),
                          (1 << 1, 'burrowed'),
                          (1 << 2, 'intransit'),
                          (1 << 3, 'hallucinated'),
                          (1 << 4, 'invincible')]:
            if sprpvalid & bit and sprpflag & bit:
                list_.append("\x1F{}".format(name))

        return "UnitProperty {}".format(' '.join(list_))

    def __init__(self):
        super().__init__()
        self.evaluated = False

    def construct_db(self):
        if not self.evaluated:
            chkt = GetChkTokenized()
            uprp = chkt.getsection('UPRP')
            upus = chkt.getsection('UPUS') or bytes([1] * 64)

            # property 0 does not affect any behavior of game.
            # just recognize color for each properties
            prop_0 = ["UnitPropertyTags"]
            prop_0.append(_PropTable.COLOR_HITPOINT + "hitpoint")
            prop_0.append(_PropTable.COLOR_SHIELD + "shield")
            prop_0.append(_PropTable.COLOR_ENERGY + "energy")
            prop_0.append(_PropTable.COLOR_RESOURCE + "resource")
            prop_0.append(_PropTable.COLOR_HANGER + "hanger")
            self.add_pair(EPDConstString(" ".join(prop_0)), 0)

            for i in range(64):
                if upus[i]:
                    uprpdata = uprp[20*i:20*i+20]
                    string = _PropTable.decode_property(uprpdata)
                    self.add_pair(EPDConstString(string), i+1)

            self.evaluated = True

    def Evaluate(self):
        self.construct_db()
        return super().Evaluate()

Property = _PropTable()
