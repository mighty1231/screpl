from eudplib import *
from screpl.writer.action import action_epd_offset_map
from . import (
    tb_scmd_player,
    tb_scmd_modifier,
    tb_scmd_score,
)

def write_scmd_action(self, act):
    assert isinstance(act, Action)

    acttype = act.fields[7]
    assert not IsEUDVariable(acttype)

    if acttype == 3:
        self.write_f("Preserve Trigger();\n")
    elif acttype == 44:
        _write_scmd__CreateUnit(self, act)
    elif acttype == 45:
        _write_scmd__SetDeaths(self, act)
    elif acttype == 27:
        _write_scmd__SetScore(self, act)
    else:
        raise RuntimeError("Unknown action type %d" % acttype)

@EUDMethod
def write_scmd_action_epd(self, epd):
    act = action_epd_offset_map(epd)
    acttype = act.acttype
    if EUDIf()(acttype == 44):
        _write_scmd__CreateUnit_epd(self, epd)
    if EUDElseIf()(acttype == 23):
        _write_scmd__KillUnitAt_epd(self, epd)
    if EUDElseIf()(acttype == 25):
        _write_scmd__RemoveUnitAt_epd(self, epd)
    if EUDElseIf()(acttype == 39):
        _write_scmd__MoveUnit_epd(self, epd)
    if EUDElse()():
        self.write_f("UNKNOWN_ACTION_TYPE_%D\n", acttype)
    EUDEndIf()

def _write_scmd__SetDeaths(self, act):
    assert act.fields[11] == 0, "eudx is currently not supported"

    self.write_f("Set Deaths(")
    self.write_scmd_const(tb_scmd_player, act.fields[4])
    self.write_f(", ")
    self.write_scmd_unit(act.fields[6])
    self.write_f(", ")
    self.write_scmd_const(tb_scmd_modifier, act.fields[8])
    self.write_f(", ")
    self.write_decimal(act.fields[5])
    self.write_f(");\n")

def _write_scmd__SetScore(self, act):
    # Set Score("Force 1", Set To, 0, Custom);
    self.write_f("Set Score(")
    self.write_scmd_const(tb_scmd_player, act.fields[4])
    self.write_f(", ")
    self.write_scmd_const(tb_scmd_modifier, act.fields[8])
    self.write_f(", ")
    self.write_decimal(act.fields[5])
    self.write_f(", ")
    self.write_scmd_const(tb_scmd_score, act.fields[6])
    self.write_f(");\n")

def _write_scmd__CreateUnit(self, act):
    # Create Unit("Players", "Unit Name", Unit Amount(#), "Location");
    self.write_f("Create Unit(")
    self.write_scmd_const(tb_scmd_player, act.fields[4])
    self.write_f(", ")
    self.write_scmd_unit(act.fields[6])
    self.write_f(", ")
    self.write_decimal(act.fields[8])
    self.write_f(", ")
    self.write_location(act.fields[0])
    self.write_f(");\n")

@EUDMethod
def _write_scmd__CreateUnit_epd(self, epd):
    # Create Unit("Players", "Unit Name", Unit Amount(#), "Location");
    m = action_epd_offset_map(epd)
    self.write_f("Create Unit(")
    self.write_scmd_const(tb_scmd_player, m.player1)
    self.write_f(", ")
    self.write_scmd_unit(m.unitid)
    self.write_f(", ")
    self.write_decimal(m.amount)
    self.write_f(", ")
    self.write_location(m.locid1)
    self.write_f(");\n")

@EUDMethod
def _write_scmd__KillUnitAt_epd(self, epd):
    # Kill Unit At Location("Players", "Unit Name", Unit Amount(#), "Location");
    m = action_epd_offset_map(epd)
    self.write_f("Kill Unit At Location(")
    self.write_scmd_const(tb_scmd_player, m.player1)
    self.write_f(", ")
    self.write_scmd_unit(m.unitid)
    self.write_f(", ")
    self.write_decimal(m.amount)
    self.write_f(", ")
    self.write_location(m.locid1)
    self.write_f(");\n")

@EUDMethod
def _write_scmd__RemoveUnitAt_epd(self, epd):
    # Remove Unit At Location("Players", "Unit Name", Unit Amount(#), "Location");
    m = action_epd_offset_map(epd)
    self.write_f("Remove Unit At Location(")
    self.write_scmd_const(tb_scmd_player, m.player1)
    self.write_f(", ")
    self.write_scmd_unit(m.unitid)
    self.write_f(", ")
    self.write_decimal(m.amount)
    self.write_f(", ")
    self.write_location(m.locid1)
    self.write_f(");\n")

@EUDMethod
def _write_scmd__MoveUnit_epd(self, epd):
    # Move Unit("Players", "Unit Name", Unit Amount(#), "Source", "Destination");
    m = action_epd_offset_map(epd)
    self.write_f("Move Unit(")
    self.write_scmd_const(tb_scmd_player, m.player1)
    self.write_f(", ")
    self.write_scmd_unit(m.unitid)
    self.write_f(", ")
    self.write_decimal(m.amount)
    self.write_f(", ")
    self.write_location(m.locid1)
    self.write_f(", ")
    self.write_location(m.player2)
    self.write_f(");\n")
