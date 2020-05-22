from eudplib import *

from screpl.utils.referencetable import SearchTableInv
from screpl.resources.table import tables as tb
from screpl.resources import offset

import screpl.main as main

_writer = None
def getWriter():
    global _writer
    if _writer is None:
        _writer = main.get_main_writer()
    return _writer

@EUDFunc
def write_constant(table_epd, val):
    name_epd = EUDVariable()
    if EUDIf()(SearchTableInv(val, table_epd, EPD(name_epd.getValueAddr())) == 1):
        getWriter().write_strepd(name_epd)
    if EUDElse()():
        getWriter().write_decimal(val)
    EUDEndIf()

@EUDFunc
def write_unit(val):
    if EUDIf()(val <= 227):
        stringid = offset.unitsdat_UnitMapString.read(val)
        if EUDIfNot()(stringid == 0):
            getWriter().write(ord('"'))
            getWriter().write_STR_string(stringid)
            getWriter().write(ord('"'))
            EUDReturn()
        EUDEndIf()
    EUDEndIf()
    getWriter().write_f("\"%E\"", tb.GetDefaultUnitNameEPDPointer(val))

@EUDFunc
def writeLocation(val):
    getWriter().write_f("\"%E\"", tb.GetLocationNameEPDPointer(val))

@EUDFunc
def writeAIScript(val):
    name_epd = EUDVariable()
    if EUDIf()(SearchTableInv(val, EPD(tb.AIScript), EPD(name_epd.getValueAddr())) == 1):
        getWriter().write_f('"%E"', name_epd)
    if EUDElse()():
        getWriter().write_decimal(val)
    EUDEndIf()

@EUDFunc
def writeSwitch(val):
    name_epd = EUDVariable()
    if EUDIf()(SearchTableInv(val, EPD(tb.swMap), EPD(name_epd.getValueAddr())) == 1):
        getWriter().write_f('"%E"', name_epd)
    if EUDElseIf()(SearchTableInv(val, EPD(tb.swSub), EPD(name_epd.getValueAddr())) == 1):
        getWriter().write_f('"%E"', name_epd)
    if EUDElse()():
        getWriter().write_decimal(val)
    EUDEndIf()

@EUDFunc
def writeString(val):
    # @TODO write partial string
    getWriter().write_decimal(val)
