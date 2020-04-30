from eudplib import *
from ...core.base import SearchTableInv
from ..table.tables import (
    tb_unit,
    tb_locSub,
    tb_swSub,
    tb_ai,
    tb_unitMap,
    tb_locMap,
    tb_swMap
)

_writer = None
def getWriter():
    global _writer
    if _writer is None:
        from ..core import getAppManager
        _writer = getAppManager().getWriter()
    return _writer

@EUDFunc
def writeConstant(table_epd, val):
    name_epd = EUDVariable()
    if EUDIf()(SearchTableInv(val, table_epd, EPD(name_epd.getValueAddr())) == 1):
        getWriter().write_strepd(name_epd)
    if EUDElse()():
        getWriter().write_decimal(val)
    EUDEndIf()

# @TODO
# \x01 ~ \x1F
# https://github.com/phu54321/TrigEditPlus/blob/master/TrigEditPlus/Editor/StringUtils/RawCStringCast.cpp

@EUDFunc
def writeUnit(val):
    name_epd = EUDVariable()
    if EUDIf()(SearchTableInv(val, EPD(tb_unitMap), EPD(name_epd.getValueAddr())) == 1):
        getWriter().write_f('"%E"', name_epd)
    if EUDElseIf()(SearchTableInv(val, EPD(tb_unit), EPD(name_epd.getValueAddr())) == 1):
        getWriter().write_f('"%E"', name_epd)
    if EUDElse()():
        getWriter().write_decimal(val)
    EUDEndIf()

@EUDFunc
def writeLocation(val):
    name_epd = EUDVariable()
    if EUDIf()(SearchTableInv(val, EPD(tb_locMap), EPD(name_epd.getValueAddr())) == 1):
        getWriter().write_f('"%E"', name_epd)
    if EUDElseIf()(SearchTableInv(val, EPD(tb_locSub), EPD(name_epd.getValueAddr())) == 1):
        getWriter().write_f('"%E"', name_epd)
    if EUDElse()():
        getWriter().write_decimal(val)
    EUDEndIf()

@EUDFunc
def writeAIScript(val):
    name_epd = EUDVariable()
    if EUDIf()(SearchTableInv(val, EPD(tb_ai), EPD(name_epd.getValueAddr())) == 1):
        getWriter().write_f('"%E"', name_epd)
    if EUDElse()():
        getWriter().write_decimal(val)
    EUDEndIf()

@EUDFunc
def writeSwitch(val):
    name_epd = EUDVariable()
    if EUDIf()(SearchTableInv(val, EPD(tb_swMap), EPD(name_epd.getValueAddr())) == 1):
        getWriter().write_f('"%E"', name_epd)
    if EUDElseIf()(SearchTableInv(val, EPD(tb_swSub), EPD(name_epd.getValueAddr())) == 1):
        getWriter().write_f('"%E"', name_epd)
    if EUDElse()():
        getWriter().write_decimal(val)
    EUDEndIf()

@EUDFunc
def writeString(val):
    # @TODO write partial string
    getWriter().write_decimal(val)
