from eudplib import *
from screpl.main import get_main_writer
from screpl.writer import write_location
from screpl.writer.action import _actmap
from . import *
from .unit import write_scmd_unit

def write_scmd_action(act):
    assert isinstance(act, Action)

    acttype = act.fields[7]
    assert not IsEUDVariable(acttype)

    if acttype == 3:
        get_main_writer().write_f("Preserve Trigger();\n")
    elif acttype == 44:
        _writeCreateUnit(act)
    elif acttype == 45:
        _writeSetDeaths(act)
    elif acttype == 27:
        _writeSetScore(act)
    else:
        raise RuntimeError("Unknown action type %d" % acttype)

@EUDFunc
def write_scmd_action_epd(epd):
    act = _actmap(epd)
    acttype = act.acttype
    if EUDIf()(acttype == 44):
        _writeCreateUnit_epd(epd)
    if EUDElseIf()(acttype == 23):
        _writeKillUnitAt_epd(epd)
    if EUDElseIf()(acttype == 25):
        _writeRemoveUnitAt_epd(epd)
    if EUDElse()():
        get_main_writer().write_f("UNKNOWN_ACTION_TYPE_%D\n", acttype)
    EUDEndIf()

def _writeSetDeaths(act):
    assert act.fields[11] == 0, "eudx is currently not supported"

    get_main_writer().write_f("Set Deaths(")
    write_scmd_player(act.fields[4])
    get_main_writer().write_f(", ")
    write_scmd_unit(act.fields[6])
    get_main_writer().write_f(", ")
    write_scmd_modifier(act.fields[8])
    get_main_writer().write_f(", ")
    write_scmd_number(act.fields[5])
    get_main_writer().write_f(");\n")

def _writeSetScore(act):
    # Set Score("Force 1", Set To, 0, Custom);
    get_main_writer().write_f("Set Score(")
    write_scmd_player(act.fields[4])
    get_main_writer().write_f(", ")
    write_scmd_modifier(act.fields[8])
    get_main_writer().write_f(", ")
    write_scmd_number(act.fields[5])
    get_main_writer().write_f(", ")
    write_scmd_score(act.fields[6])
    get_main_writer().write_f(");\n")

def _writeCreateUnit(act):
    # Create Unit("Players", "Unit Name", Unit Amount(#), "Location");
    get_main_writer().write_f("Create Unit(")
    write_scmd_player(act.fields[4])
    get_main_writer().write_f(", ")
    write_scmd_unit(act.fields[6])
    get_main_writer().write_f(", ")
    write_scmd_number(act.fields[8])
    get_main_writer().write_f(", ")
    write_location(act.fields[0])
    get_main_writer().write_f(");\n")

@EUDFunc
def _writeCreateUnit_epd(epd):
    # Create Unit("Players", "Unit Name", Unit Amount(#), "Location");
    m = _actmap(epd)
    get_main_writer().write_f("Create Unit(")
    write_scmd_player(m.player1)
    get_main_writer().write_f(", ")
    write_scmd_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_scmd_number(m.amount)
    get_main_writer().write_f(", ")
    write_location(m.locid1)
    get_main_writer().write_f(");\n")

@EUDFunc
def _writeKillUnitAt_epd(epd):
    # Kill Unit At Location("Players", "Unit Name", Unit Amount(#), "Location");
    m = _actmap(epd)
    get_main_writer().write_f("Kill Unit At Location(")
    write_scmd_player(m.player1)
    get_main_writer().write_f(", ")
    write_scmd_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_scmd_number(m.amount)
    get_main_writer().write_f(", ")
    write_location(m.locid1)
    get_main_writer().write_f(");\n")

@EUDFunc
def _writeRemoveUnitAt_epd(epd):
    # Remove Unit At Location("Players", "Unit Name", Unit Amount(#), "Location");
    m = _actmap(epd)
    get_main_writer().write_f("Remove Unit At Location(")
    write_scmd_player(m.player1)
    get_main_writer().write_f(", ")
    write_scmd_unit(m.unitid)
    get_main_writer().write_f(", ")
    write_scmd_number(m.amount)
    get_main_writer().write_f(", ")
    write_location(m.locid1)
    get_main_writer().write_f(");\n")
