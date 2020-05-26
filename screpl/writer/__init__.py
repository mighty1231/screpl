from eudplib import *

from screpl.utils.referencetable import search_table_inv
from screpl.resources.table import tables as tb
from screpl.resources import offset

import screpl.main as main

_writer = None
def get_main_writer():
    global _writer
    if _writer is None:
        _writer = main.get_main_writer()
    return _writer

@EUDFunc
def write_constant(table_epd, val):
    name_epd = EUDVariable()
    if EUDIf()(search_table_inv(val, table_epd, EPD(name_epd.getValueAddr())) == 1):
        get_main_writer().write_strepd(name_epd)
    if EUDElse()():
        get_main_writer().write_decimal(val)
    EUDEndIf()

@EUDFunc
def write_unit(val):
    if EUDIf()(val <= 227):
        stringid = offset.unitsdat_UnitMapString.read(val)
        if EUDIfNot()(stringid == 0):
            get_main_writer().write(ord('"'))
            get_main_writer().write_strx_string(stringid)
            get_main_writer().write(ord('"'))
            EUDReturn()
        EUDEndIf()
    EUDEndIf()
    get_main_writer().write_f("\"%E\"", tb.GetDefaultUnitNameEPDPointer(val))

@EUDFunc
def write_location(val):
    get_main_writer().write_f("\"%E\"", tb.GetLocationNameEPDPointer(val))

@EUDFunc
def write_aiscript(val):
    name_epd = EUDVariable()
    if EUDIf()(search_table_inv(val, EPD(tb.AIScript), EPD(name_epd.getValueAddr())) == 1):
        get_main_writer().write_f('"%E"', name_epd)
    if EUDElse()():
        get_main_writer().write_decimal(val)
    EUDEndIf()

@EUDFunc
def write_switch(val):
    name_epd = EUDVariable()
    if EUDIf()(search_table_inv(val, EPD(tb.swMap), EPD(name_epd.getValueAddr())) == 1):
        get_main_writer().write_f('"%E"', name_epd)
    if EUDElseIf()(search_table_inv(val, EPD(tb.swSub), EPD(name_epd.getValueAddr())) == 1):
        get_main_writer().write_f('"%E"', name_epd)
    if EUDElse()():
        get_main_writer().write_decimal(val)
    EUDEndIf()

@EUDFunc
def write_string(val):
    # @TODO write partial string
    get_main_writer().write_decimal(val)
