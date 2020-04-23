from eudplib import *

class Offset:
    def __init__(self, base, itemsz):
        assert base % 4 == 0 and itemsz in [1, 2, 4]
        self.base = base
        self.itemsz = itemsz

    def read(self, idx):
        off = self.base + self.itemsz * idx
        if self.itemsz == 4:
            return f_dwread_epd(EPD(off))
        elif self.itemsz == 2:
            r = off % 4
            return f_wread_epd(EPD(off), r)
        # byte
        r = off % 4
        return f_bread_epd(EPD(off), r)

    def write(self, idx, value):
        off = self.base + self.itemsz * idx
        if self.itemsz == 4:
            return f_dwwrite_epd(EPD(off), value)
        elif self.itemsz == 2:
            r = off % 4
            return f_wwrite_epd(EPD(off), r, value)
        # byte
        r = off % 4
        return f_bwrite_epd(EPD(off), r, value)

off_unitsdat_UnitMapString = Offset(0x660260, 2)
