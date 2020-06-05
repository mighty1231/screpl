"""TrigEntry"""

from eudplib import *

from screpl.utils.struct import REPLStruct
from screpl.utils.conststring import EPDConstString

class TrigEntry(REPLStruct):
    fields = [
        "name_epd",
        "offset_epd",
        "offset_rem",
        "size",
    ]

    @staticmethod
    def construct(name, offset, size):
        obj = TrigEntry.initialize_with(
            EPDConstString(name),
            offset // 4,
            offset % 4,
            size,
        )
        return obj

    def write_bytes(self, writer, obj_epd):
        offset_epd = obj_epd + self.offset_epd
        offset_rem = self.offset_rem
        size = self.size

        if EUDIf()(size == 1):
            writer.write_memory_table_epd(offset_epd,
                                          offset_rem, 1)
        if EUDElseIf()(size == 2):
            writer.write_memory_table_epd(offset_epd,
                                          offset_rem, 2)
        if EUDElse()():
            writer.write_memory_table_epd(offset_epd,
                                          0, 4)
        EUDEndIf()

    @EUDMethod
    def set_value(self, obj_epd, value):
        offset_epd = obj_epd + self.offset_epd
        offset_rem = self.offset_rem
        size = self.size

        if EUDIf()(size == 1):
            f_bwrite_epd(offset_epd, offset_rem, value)
        if EUDElseIf()(size == 2):
            f_wwrite_epd(offset_epd, offset_rem, value)
        if EUDElse()():
            f_dwwrite_epd(offset_epd, value)
        EUDEndIf()