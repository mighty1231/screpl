from eudplib import *

from ..core.app import Application, getAppManager, AppCommand
from ..utils import EPDConstStringArray

_location = EUDVariable(1)

class LocationApp(Application):
    fields = [
        "location", # 1 ~ 255

        "centerview", # do centerview every setLocation if 1
        "autorefresh", # read location every loop if 1

        "frame"
    ]

    @staticmethod
    def setContent(location):
        _location << EncodeLocation(location)

    def init(self):
        self.location = _location
        self.centerview = 1
        self.autorefresh = 1
        self.frame = 0
        
        # make enable to create Scanner Sweep
        DoActions(SetMemoryX(0x661558, SetTo, 1 << 17, 1 << 17))

    def setLocation(self, location):
        if EUDIf()([location >= 1, location <= 255]):
            if EUDIfNot()(location == self.location):
                self.location = location

                if EUDIfNot()(self.centerview == 0):
                    cp = f_getcurpl()
                    f_setcurpl(getAppManager().superuser)
                    DoActions([CenterView(location)])
                    f_setcurpl(cp)
                EUDEndIf()
                getAppManager().requestUpdate()
            EUDEndIf()
        EUDEndIf()

    def loop(self):
        # F7 - previous location
        # F8 - next location
        manager = getAppManager()
        location = self.location
        superuser = manager.superuser
        if EUDIf()(manager.keyPress("ESC")):
            manager.requestDestruct()
        if EUDElseIf()(manager.keyPress("F7")):
            self.setLocation(location - 1)
        if EUDElseIf()(manager.keyPress("F8")):
            self.setLocation(location + 1)
        EUDEndIf()

        if EUDIfNot()(self.autorefresh == 0):
            manager.requestUpdate()
        EUDEndIf()


        # backup Scanner Sweep and prepare effect
        prev_im = f_dwread_epd(EPD(0x666458))
        prev_is = f_dwread_epd(EPD(0x66EFE8))
        DoActions([
            # Set Scanner Sweep to image 232 Nuke Beam
            SetMemoryX(0x666458, SetTo, 232, 0xFFFF),

            # image_232_iscript, disappeared after 1 frame
            SetMemory(0x66EFE8, SetTo, 250) 
        ])

        # draw location with Scanner Sweep
        cur_epd = EPD(0x58DC60 - 0x14) + (0x14 // 4) * self.location
        le, te, re, de = cur_epd, cur_epd+1, cur_epd+2, cur_epd+3
        l, t, r, d = [f_dwread_epd(ee) for ee in [le, te, re, de]]

        # @TODO draw rectangle more elgant way
        f_dwwrite_epd(de, t) # N
        DoActions(CreateUnit(1, "Scanner Sweep", location, superuser))
        f_dwwrite_epd(le, r) # NE
        DoActions(CreateUnit(1, "Scanner Sweep", location, superuser))
        f_dwwrite_epd(de, d) # E
        DoActions(CreateUnit(1, "Scanner Sweep", location, superuser))
        f_dwwrite_epd(te, d) # SE
        DoActions(CreateUnit(1, "Scanner Sweep", location, superuser))
        f_dwwrite_epd(le, l) # S
        DoActions(CreateUnit(1, "Scanner Sweep", location, superuser))
        f_dwwrite_epd(re, l) # SW
        DoActions(CreateUnit(1, "Scanner Sweep", location, superuser))
        f_dwwrite_epd(te, t) # W
        DoActions(CreateUnit(1, "Scanner Sweep", location, superuser))
        f_dwwrite_epd(de, t) # NW
        DoActions(CreateUnit(1, "Scanner Sweep", location, superuser))

        # restore location
        for epd, val in zip([le, te, re, de], [l, t, r, d]):
            f_dwwrite_epd(epd, val)

        # restore Scanner Sweep
        DoActions([
            RemoveUnit("Scanner Sweep", superuser),
            SetMemoryX(0x666458, SetTo, prev_im, 0xFFFF),
            SetMemory(0x66EFE8, SetTo, prev_is)
        ])

    @AppCommand([])
    def toggle_cv(self):
        if EUDIfNot()(self.centerview == 0):
            self.centerview = 0
        if EUDElse()():
            self.centerview = 1
        EUDEndIf()
        getAppManager().requestUpdate()

    @AppCommand([])
    def toggle_ar(self):
        if EUDIfNot()(self.autorefresh == 0):
            self.autorefresh = 0
        if EUDElse()():
            self.autorefresh = 1
        EUDEndIf()

    def print(self, writer):
        # title
        writer.write_f("Location (Left, Top, Right, Down, Flag, Name) ( %D / 256 ) // CenterView: ",
                self.location)
        if EUDIfNot()(self.centerview == 0):
            writer.write_f("ON\n")
        if EUDElse()():
            writer.write_f("OFF\n")
        EUDEndIf()

        target_location = self.location

        quot, mod = f_div(target_location - 1, 8)
        cur = quot * 8 + 1
        until = cur + 8
        if EUDIf()(until == 255):
            until << 254
        EUDEndIf()

        # fill
        cur_epd = EPD(0x58DC60 - 0x14) + (0x14 // 4) * cur
        cur_ptr = (0x58DC60 - 0x14) + 0x14 * cur
        if EUDInfLoop()():
            EUDBreakIf(cur >= until)
            # "(color)(locid) (ptr): (left) (top) (right) (down) (flag) (string)
            # +0x00: X1, +0x04: Y1, +0x08: X2, +0x0C: Y2, +0x10: StringID, +0x12: Flags
            left = f_dwread_epd(cur_epd)
            top = f_dwread_epd(cur_epd + 1)
            right = f_dwread_epd(cur_epd + 2)
            down = f_dwread_epd(cur_epd + 3)
            strId = f_wread_epd(cur_epd + 4, 0)
            flag = f_wread_epd(cur_epd + 4, 2)

            if EUDIf()(cur == target_location):
                writer.write(0x11) # orange
            if EUDElse()():
                writer.write(0x02) # pale blue
            EUDEndIf()
            writer.write_f(" %D %H : %D %D %D %D ",
                cur, cur_ptr, left, top, right, down
            )
            writer.write_binary(flag)
            writer.write(ord(' '))
            if EUDIfNot()(strId == 0):
                writer.write_STR_string(strId)
            EUDEndIf()
            writer.write(ord('\n'))

            DoActions([cur_ptr.AddNumber(0x14), cur.AddNumber(1), cur_epd.AddNumber(0x14//4)])
        EUDEndInfLoop()

        writer.write(0)
