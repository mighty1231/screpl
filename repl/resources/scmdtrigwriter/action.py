from eudplib import *
from ..writer import writeUnit, writeLocation
from ..writer.action import _actmap
from . import *

def SCMDWriteAction(act):
    assert isinstance(act, Action)
    
    acttype = act.fields[7]
    assert not IsEUDVariable(acttype)

    if acttype == 3:
        getWriter().write_f("Preserve Trigger();\n")
    elif acttype == 45:
        _writeSetDeaths(act)
    else:
        print("WARNING: Unknown action type %d" % acttype)

@EUDFunc
def SCMDWriteAction_epd(epd):
    act = _actmap(epd)
    acttype = act.acttype
    if EUDIf()(acttype == 44):
        _writeCreateUnit_epd(epd)
    if EUDElseIf()(acttype == 23):
        _writeKillUnitAt_epd(epd)
    if EUDElseIf()(acttype == 25):
        _writeRemoveUnitAt_epd(epd)
    if EUDElse()():
        getWriter().write_f("UNKNOWN_ACTION_TYPE_%D\n", acttype)
    EUDEndIf()

def _writeSetDeaths(act):
    assert act.fields[11] == 0, "eudx is currently not supported"

    getWriter().write_f("Set Deaths(")
    SCMDDecoder_Player(act.fields[4])
    getWriter().write_f(", ")
    writeUnit(act.fields[6])
    getWriter().write_f(", ")
    SCMDDecoder_Modifier(act.fields[8])
    getWriter().write_f(", ")
    SCMDDecoder_Number(act.fields[5])
    getWriter().write_f(");\n")

_actmap = EPDOffsetMap((
    ('locid1', 0x00, 4),
    ('strid', 0x04, 4),
    ('wavid', 0x08, 4),
    ('time', 0x0C, 4),
    ('player1', 0x10, 4),
    ('player2', 0x14, 4),
    ('unitid', 0x18, 2),
    ('acttype', 0x1A, 1),
    ('amount', 0x1B, 1),
    ('flags', 0x1C, 1),
    ('internal', 0x1E, 2),
))
@EUDFunc
def _writeCreateUnit_epd(epd):
    # Create Unit("Players", "Unit Name", Unit Amount(#), "Location");
    m = _actmap(epd)
    getWriter().write_f("Create Unit(")
    SCMDDecoder_Player(m.player1)
    getWriter().write_f(", ")
    writeUnit(m.unitid)
    getWriter().write_f(", ")
    SCMDDecoder_Number(m.amount)
    getWriter().write_f(", ")
    writeLocation(m.locid1)
    getWriter().write_f(");\n")

@EUDFunc
def _writeKillUnitAt_epd(epd):
    # Kill Unit At Location("Players", "Unit Name", Unit Amount(#), "Location");
    m = _actmap(epd)
    getWriter().write_f("Kill Unit At Location(")
    SCMDDecoder_Player(m.player1)
    getWriter().write_f(", ")
    writeUnit(m.unitid)
    getWriter().write_f(", ")
    SCMDDecoder_Number(m.amount)
    getWriter().write_f(", ")
    writeLocation(m.locid1)
    getWriter().write_f(");\n")

@EUDFunc
def _writeRemoveUnitAt_epd(epd):
    # Remove Unit At Location("Players", "Unit Name", Unit Amount(#), "Location");
    m = _actmap(epd)
    getWriter().write_f("Remove Unit At Location(")
    SCMDDecoder_Player(m.player1)
    getWriter().write_f(", ")
    writeUnit(m.unitid)
    getWriter().write_f(", ")
    SCMDDecoder_Number(m.amount)
    getWriter().write_f(", ")
    writeLocation(m.locid1)
    getWriter().write_f(");\n")
