from eudplib import *
from ..writer import writeLocation
from ..writer.condition import _condmap
from . import *
from .unit import SCMDWriteUnit

def SCMDWriteCondition(cond):
    assert isinstance(cond, Condition)
    
    condtype = cond.fields[5]
    assert not IsEUDVariable(condtype)

    if condtype == 2:
        _writeCommand(cond)
    elif condtype == 15:
        _writeDeaths(cond)
    elif condtype == 22:
        getWriter().write_f("Always();\n")
    else:
        raise RuntimeError("Unknown condition type %d" % condtype)

def _writeDeaths(cond):
    assert cond.fields[8] == 0, "eudx is currently not supported"

    getWriter().write_f("Deaths(")
    SCMDWritePlayer(cond.fields[1])
    getWriter().write_f(", ")
    SCMDWriteUnit(cond.fields[3])
    getWriter().write_f(", ")
    SCMDWriteComparison(cond.fields[4])
    getWriter().write_f(", ")
    SCMDWriteNumber(cond.fields[2])
    getWriter().write_f(");\n")

def _writeCommand(cond):
    getWriter().write_f("Command(")
    SCMDWritePlayer(cond.fields[1])
    getWriter().write_f(", ")
    SCMDWriteUnit(cond.fields[3])
    getWriter().write_f(", ")
    SCMDWriteComparison(cond.fields[4])
    getWriter().write_f(", ")
    SCMDWriteNumber(cond.fields[2])
    getWriter().write_f(");\n")
