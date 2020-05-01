from eudplib import *

from ...base import SearchTableInv
from ..table.tables import (
    GetDefaultUnitNameEPDPointer,
    GetLocationNameEPDPointer,
    tb_swMap,
    tb_swSub,
    tb_AIScript
)
from ..offset import off_unitsdat_UnitMapString

_writer = None
def getWriter():
    global _writer
    if _writer is None:
        from ...core import getAppManager
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

@EUDFunc
def writeUnit(val):
    if EUDIf()(val <= 227):
        stringid = off_unitsdat_UnitMapString.read(val)
        if EUDIfNot()(stringid == 0):
            getWriter().write_STR_string(stringid)
            EUDReturn()
        EUDEndIf()
    EUDEndIf()
    getWriter().write_strepd(GetDefaultUnitNameEPDPointer(val))

@EUDFunc
def writeLocation(val):
    getWriter().write_strepd(GetLocationNameEPDPointer(val))

@EUDFunc
def writeAIScript(val):
    name_epd = EUDVariable()
    if EUDIf()(SearchTableInv(val, EPD(tb_AIScript), EPD(name_epd.getValueAddr())) == 1):
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
