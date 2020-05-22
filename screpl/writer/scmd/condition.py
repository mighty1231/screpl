from eudplib import *
from screpl.main import get_main_writer
from screpl.writer import writeLocation
from screpl.writer.condition import _condmap
from . import *
from .unit import write_scmdunit

def SCMDWriteCondition(cond):
    assert isinstance(cond, Condition)
    
    condtype = cond.fields[5]
    assert not IsEUDVariable(condtype)

    if condtype == 2:
        _writeCommand(cond)
    elif condtype == 15:
        _writeDeaths(cond)
    elif condtype == 22:
        get_main_writer().write_f("Always();\n")
    else:
        raise RuntimeError("Unknown condition type %d" % condtype)

def _writeDeaths(cond):
    assert cond.fields[8] == 0, "eudx is currently not supported"

    get_main_writer().write_f("Deaths(")
    SCMDWritePlayer(cond.fields[1])
    get_main_writer().write_f(", ")
    write_scmdunit(cond.fields[3])
    get_main_writer().write_f(", ")
    SCMDWriteComparison(cond.fields[4])
    get_main_writer().write_f(", ")
    SCMDWriteNumber(cond.fields[2])
    get_main_writer().write_f(");\n")

def _writeCommand(cond):
    get_main_writer().write_f("Command(")
    SCMDWritePlayer(cond.fields[1])
    get_main_writer().write_f(", ")
    write_scmdunit(cond.fields[3])
    get_main_writer().write_f(", ")
    SCMDWriteComparison(cond.fields[4])
    get_main_writer().write_f(", ")
    SCMDWriteNumber(cond.fields[2])
    get_main_writer().write_f(");\n")
