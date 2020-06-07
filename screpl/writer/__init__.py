from eudplib import *

from screpl.utils.referencetable import search_table_inv
from screpl.resources.table import tables as tb
from screpl.resources import offset

@EUDMethod
def write_constant(self, table_epd, val):
    name_epd = EUDVariable()
    if EUDIf()(search_table_inv(val,
                                table_epd,
                                EPD(name_epd.getValueAddr())) == 1):
        self.write_strepd(name_epd)
    if EUDElse()():
        self.write_decimal(val)
    EUDEndIf()

@EUDMethod
def write_unit(self, val):
    if EUDIf()(val <= 227):
        stringid = offset.unitsdat_UnitMapString.read(val)
        if EUDIfNot()(stringid == 0):
            self.write(ord('"'))
            self.write_strx_string(stringid)
            self.write(ord('"'))
            EUDReturn()
        EUDEndIf()
    EUDEndIf()
    self.write_f('"%E"', tb.get_default_unitname_epd(val))

@EUDMethod
def write_location(self, val):
    if EUDIf()([val >= 1, val <= 255]):
        name_epd = tb.get_locationname_epd(val)
        self.write_f('"%E"', name_epd)
    if EUDElse()():
        self.write_decimal(val)
    EUDEndIf()

@EUDMethod
def write_aiscript(self, val):
    name_epd = EUDVariable()
    if EUDIf()(search_table_inv(val,
                                EPD(tb.AIScript),
                                EPD(name_epd.getValueAddr())) == 1):
        self.write_f('"%E"', name_epd)
    if EUDElse()():
        self.write_decimal(val)
    EUDEndIf()

@EUDMethod
def write_switch(self, val):
    if EUDIf()(val <= 256):
        name_epd = tb.get_switchname_epd(val)
        self.write_f('"%E"', name_epd)
    if EUDElse()():
        self.write_decimal(val)
    EUDEndIf()

@EUDMethod
def write_string(self, val):
    # @TODO write partial string
    self.write_decimal(val)

def writer_init():
    from screpl.utils.byterw import REPLByteRW

    from screpl.writer.action import writer_action_init
    from screpl.writer.condition import writer_condition_init
    from screpl.writer.scmd import writer_scmd_init

    REPLByteRW.add_method(write_constant)
    REPLByteRW.add_method(write_unit)
    REPLByteRW.add_method(write_location)
    REPLByteRW.add_method(write_aiscript)
    REPLByteRW.add_method(write_switch)
    REPLByteRW.add_method(write_string)

    writer_condition_init()
    writer_action_init()
    writer_scmd_init()
