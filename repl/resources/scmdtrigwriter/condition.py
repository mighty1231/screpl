from eudplib import *
from ..writer import writeUnit, writeLocation
from ..writer.condition import _condmap
from . import *

def SCMDWriteCondition(cond):
    assert isinstance(cond, Condition)
    
    condtype = cond.fields[5]
    assert not IsEUDVariable(condtype)

    if condtype == 22:
        getWriter().write_f("Always();\n")
    elif condtype == 15:
        _writeDeaths(cond)
    else:
        print("WARNING: Unknown condition type %d" % condtype)

def _writeDeaths(cond):
    assert cond.fields[8] == 0, "eudx is currently not supported"

    getWriter().write_f("Deaths(")
    SCMDDecoder_Player(cond.fields[1])
    getWriter().write_f(", ")
    writeUnit(cond.fields[3])
    getWriter().write_f(", ")
    SCMDDecoder_Comparison(cond.fields[4])
    getWriter().write_f(", ")
    SCMDDecoder_Number(cond.fields[2])
    getWriter().write_f(");\n")
