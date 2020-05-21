from eudplib import *
from ..writer import writeLocation
from ..writer.action import _actmap
from . import *
from .unit import write_scmdunit

def write_scmdaction(act):
    assert isinstance(act, Action)
    
    acttype = act.fields[7]
    assert not IsEUDVariable(acttype)

    if acttype == 3:
        getWriter().write_f("Preserve Trigger();\n")
    elif acttype == 44:
        _writeCreateUnit(act)
    elif acttype == 45:
        _writeSetDeaths(act)
    elif acttype == 27:
        _writeSetScore(act)
    else:
        raise RuntimeError("Unknown action type %d" % acttype)

@EUDFunc
def SCMDwrite_action_epd(epd):
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
    SCMDWritePlayer(act.fields[4])
    getWriter().write_f(", ")
    write_scmdunit(act.fields[6])
    getWriter().write_f(", ")
    SCMDWriteModifier(act.fields[8])
    getWriter().write_f(", ")
    SCMDWriteNumber(act.fields[5])
    getWriter().write_f(");\n")

def _writeSetScore(act):
    # Set Score("Force 1", Set To, 0, Custom);
    getWriter().write_f("Set Score(")
    SCMDWritePlayer(act.fields[4])
    getWriter().write_f(", ")
    SCMDWriteModifier(act.fields[8])
    getWriter().write_f(", ")
    SCMDWriteNumber(act.fields[5])
    getWriter().write_f(", ")
    SCMDWriteScore(act.fields[6])
    getWriter().write_f(");\n")

def _writeCreateUnit(act):
    # Create Unit("Players", "Unit Name", Unit Amount(#), "Location");
    getWriter().write_f("Create Unit(")
    SCMDWritePlayer(act.fields[4])
    getWriter().write_f(", ")
    write_scmdunit(act.fields[6])
    getWriter().write_f(", ")
    SCMDWriteNumber(act.fields[8])
    getWriter().write_f(", ")
    writeLocation(act.fields[0])
    getWriter().write_f(");\n")

@EUDFunc
def _writeCreateUnit_epd(epd):
    # Create Unit("Players", "Unit Name", Unit Amount(#), "Location");
    m = _actmap(epd)
    getWriter().write_f("Create Unit(")
    SCMDWritePlayer(m.player1)
    getWriter().write_f(", ")
    write_scmdunit(m.unitid)
    getWriter().write_f(", ")
    SCMDWriteNumber(m.amount)
    getWriter().write_f(", ")
    writeLocation(m.locid1)
    getWriter().write_f(");\n")

@EUDFunc
def _writeKillUnitAt_epd(epd):
    # Kill Unit At Location("Players", "Unit Name", Unit Amount(#), "Location");
    m = _actmap(epd)
    getWriter().write_f("Kill Unit At Location(")
    SCMDWritePlayer(m.player1)
    getWriter().write_f(", ")
    write_scmdunit(m.unitid)
    getWriter().write_f(", ")
    SCMDWriteNumber(m.amount)
    getWriter().write_f(", ")
    writeLocation(m.locid1)
    getWriter().write_f(");\n")

@EUDFunc
def _writeRemoveUnitAt_epd(epd):
    # Remove Unit At Location("Players", "Unit Name", Unit Amount(#), "Location");
    m = _actmap(epd)
    getWriter().write_f("Remove Unit At Location(")
    SCMDWritePlayer(m.player1)
    getWriter().write_f(", ")
    write_scmdunit(m.unitid)
    getWriter().write_f(", ")
    SCMDWriteNumber(m.amount)
    getWriter().write_f(", ")
    writeLocation(m.locid1)
    getWriter().write_f(");\n")
