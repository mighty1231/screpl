from eudplib import *

from repl import (
    Application,
    getAppManager,
    AppCommand,
    EPDConstString
)

from .rect import drawRectangle


_location = EUDVariable(1)

FRAME_PERIOD = 24
locstrings = None
mapw = -1
maph = -1

class LocationApp(Application):
    fields = [
        "location", # 1 ~ 255

        "centerview", # do centerview every setLocation if 1
        "autorefresh", # read location every loop if 1

        "frame"
    ]

    @classmethod
    def allocate(cls):
        if not cls._allocated_:
            global mapw, maph, locstrings
            if mapw == -1:
                from eudplib.core.mapdata.stringmap import locmap
                arr = [0 for _ in range(256)]
                for string, locid in locmap._s2id.items():
                    arr[locid + 1] = EPDConstString(string)
                locstrings = EUDArray(arr)
                dim = GetChkTokenized().getsection(b'DIM ')
                mapw = b2i2(dim, 0)
                maph = b2i2(dim, 2)

            DoActions([
                # make enable to create Scanner Sweep
                SetMemoryX(0x661558, SetTo, 1 << 17, 1 << 17),

                # unit dimension
                SetMemory(0x6617C8 + 33 * 8, SetTo, 0x00040004),
                SetMemory(0x6617C8 + 33 * 8 + 4, SetTo, 0x00040004)
            ])
        super(LocationApp, cls).allocate()

    @staticmethod
    def setContent(location):
        _location << EncodeLocation(location)

    def init(self):
        global mapw
        assert mapw != -1
        self.location = 0
        self.centerview = 1
        self.autorefresh = 1
        self.frame = 0

        self.setLocation(_location)

    def setLocation(self, location):
        if EUDIf()([location >= 1, location <= 255]):
            if EUDIfNot()(location == self.location):
                self.frame = 0
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
        drawRectangle(location, self.frame, FRAME_PERIOD, mapw, maph)

        # restore Scanner Sweep
        DoActions([
            RemoveUnit("Scanner Sweep", superuser),
            SetMemoryX(0x666458, SetTo, prev_im, 0xFFFF),
            SetMemory(0x66EFE8, SetTo, prev_is)
        ])

        self.frame += 1
        if EUDIf()(self.frame == FRAME_PERIOD):
            self.frame = 0
        EUDEndIf()

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
        writer.write_f("Location (sizeX, sizeY, flags) ( %D / 256 ) // CenterView: ",
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
            # flags
            #   0x01: Low Ground
            #   0x02: Med Ground
            #   0x04: High Ground
            #   0x08: Low Air
            #   0x10: Med Air
            #   0x20: High Air
            left  = f_dwread_epd(cur_epd)
            top   = f_dwread_epd(cur_epd + 1)
            right = f_dwread_epd(cur_epd + 2)
            down  = f_dwread_epd(cur_epd + 3)
            flag = f_wread_epd(cur_epd + 4, 2)

            if EUDIf()(cur == target_location):
                writer.write(0x11) # orange
            if EUDElse()():
                writer.write(0x02) # pale blue
            EUDEndIf()

            str_epd = locstrings[cur]
            if EUDIfNot()(str_epd == 0):
                writer.write_f(" %D '%E': %D x %D // ", cur, str_epd, right-left, down-top)
            if EUDElse()():
                writer.write_f(" %D: %D x %D // ", cur, right-left, down-top)
            EUDEndIf()

            layers = ['Low Ground', 'Med Ground', 'High Ground',
                    'Low Air', 'Med Air', 'High Air']
            if EUDIf()(flag.Exactly(0)):
                writer.write_f("All")
            if EUDElse()():
                cnt = EUDVariable()
                cnt << 0
                for i, layer in enumerate(layers):
                    if EUDIf()(flag.ExactlyX(1 << i, 1 << i)):
                        if EUDIf()(cnt >= 1):
                            writer.write_f(", ")
                        EUDEndIf()
                        writer.write_f(layer)
                        cnt += 1
                    EUDEndIf()
            EUDEndIf()
            writer.write(ord('\n'))

            DoActions([cur_ptr.AddNumber(0x14), cur.AddNumber(1), cur_epd.AddNumber(0x14//4)])
        EUDEndInfLoop()

        writer.write(0)
