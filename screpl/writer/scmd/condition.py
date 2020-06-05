from eudplib import *
from . import (
    tb_scmd_comparison,
    tb_scmd_player,
)

def write_scmd_condition(self, cond):
    assert isinstance(cond, Condition)

    condtype = cond.fields[5]
    assert not IsEUDVariable(condtype)

    if condtype == 2:
        _write_scmd__Command(self, cond)
    elif condtype == 15:
        _write_scmd__Deaths(self, cond)
    elif condtype == 22:
        self.write_f("Always();\n")
    else:
        raise RuntimeError("Unknown condition type %d" % condtype)

def _write_scmd__Deaths(self, cond):
    assert cond.fields[8] == 0, "eudx is currently not supported"

    self.write_f("Deaths(")
    self.write_scmd_const(tb_scmd_player, cond.fields[1])
    self.write_f(", ")
    self.write_scmd_unit(cond.fields[3])
    self.write_f(", ")
    self.write_scmd_const(tb_scmd_comparison, cond.fields[4])
    self.write_f(", ")
    self.write_decimal(cond.fields[2])
    self.write_f(");\n")

def _write_scmd__Command(self, cond):
    self.write_f("Command(")
    self.write_scmd_const(tb_scmd_player, cond.fields[1])
    self.write_f(", ")
    self.write_scmd_unit(cond.fields[3])
    self.write_f(", ")
    self.write_scmd_const(tb_scmd_comparison, cond.fields[4])
    self.write_f(", ")
    self.write_decimal(cond.fields[2])
    self.write_f(");\n")
