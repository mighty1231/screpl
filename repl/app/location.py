from eudplib import *

from ..core.app import Application, getAppManager, AppCommand

_location = EUDVariable(1)
mapw = -1
maph = -1
FRAME_PERIOD = 24

def drawRectangle(location, frame):
    superuser = getAppManager().superuser

    cur_epd = EPD(0x58DC60 - 0x14) + (0x14 // 4) * location
    le, te, re, de = cur_epd, cur_epd+1, cur_epd+2, cur_epd+3
    lv, tv, rv, dv = [f_dwread_epd(ee) for ee in [le, te, re, de]]

    # 0, 0, 0, 0: pass
    # size 0 -> draw '+'
    # run under each side
    #    length == 0  -> draw point
    #    length <= 32 -> draw 3 points (start, end, mid)
    #    length >  32 -> draw 5 points with interval 8 pixels
    #                    , moves length / 24 for every single frame
    #                    ((frame * length / 24) + offset) % length
    mark = lambda: DoActions(CreateUnit(1, "Scanner Sweep", location, superuser))
    end_point = Forward()

    # not a location
    EUDJumpIf(lv >= mapw * 32, end_point)
    EUDJumpIf(rv >= mapw * 32, end_point)
    EUDJumpIf(tv >= maph * 32, end_point)
    EUDJumpIf(dv >= maph * 32, end_point)

    i, end = EUDCreateVariables(2)
    if EUDIf()([lv == rv, tv == dv]):
        if EUDIfNot()([lv == 0, tv == 0]):
            # draw '+'
            i << lv - 16
            end << lv + 16
            if EUDWhile()([i <= end]):
                if EUDIf()([i > 0]):
                    f_dwwrite_epd(le, i)
                    f_dwwrite_epd(re, i)
                    mark()
                EUDEndIf()
                i += 2
            EUDEndWhile()

            f_dwwrite_epd(le, lv)
            f_dwwrite_epd(re, rv)

            i << tv - 16
            end << tv + 16
            if EUDWhile()([i <= end]):
                if EUDIf()([i > 0]):
                    f_dwwrite_epd(te, i)
                    f_dwwrite_epd(de, i)
                    mark()
                EUDEndIf()
                i += 2
            EUDEndWhile()
        EUDEndIf()
        EUDJump(end_point)
    EUDEndIf()

    # ((frame * length / 24) + offset) % length
    length = EUDVariable()
    bias = EUDVariable()

    @EUDFunc
    def plus(bias, length, _from, _to, epd1, epd2):
        i = _from + bias
        if EUDLoopN()(5):
            f_dwwrite_epd(epd1, i)
            f_dwwrite_epd(epd2, i)
            DoActions(CreateUnit(1, "Scanner Sweep", location, superuser))

            i += 8
            if EUDIf()(i > _to):
                i -= length
            EUDEndIf()
        EUDEndLoopN()

    @EUDFunc
    def minus(bias, length, _from, _to, epd1, epd2):
        i = _from - bias
        if EUDLoopN()(5):
            f_dwwrite_epd(epd1, i)
            f_dwwrite_epd(epd2, i)
            DoActions(CreateUnit(1, "Scanner Sweep", location, superuser))

            i -= 8
            if EUDIf()(i < _to):
                i += length
            EUDEndIf()
        EUDEndLoopN()

    if EUDIf()(lv < rv - 32):
        length << rv - lv
        bias << (frame * length) // FRAME_PERIOD

        f_dwwrite_epd(de, tv)
        plus(bias, length, lv, rv, le, re)

        f_dwwrite_epd(te, dv)
        f_dwwrite_epd(de, dv)
        minus(bias, length, rv, lv, le, re)
    if EUDElseIf()(lv == rv):
        f_dwwrite_epd(de, tv)
        mark()

        f_dwwrite_epd(te, dv)
        f_dwwrite_epd(de, dv)
        mark()
    if EUDElseIf()(lv > rv + 32):
        length << lv - rv
        bias << (frame * length) // FRAME_PERIOD

        f_dwwrite_epd(de, tv)
        minus(bias, length, lv, rv, le, re)

        f_dwwrite_epd(te, dv)
        f_dwwrite_epd(de, dv)
        plus(bias, length, rv, lv, le, re)
    if EUDElse()():
        f_dwwrite_epd(de, tv)
        mark()
        f_dwwrite_epd(re, lv)
        mark()
        f_dwwrite_epd(le, rv)
        f_dwwrite_epd(re, rv)
        mark()

        f_dwwrite_epd(te, dv)
        f_dwwrite_epd(de, dv)
        mark()
        f_dwwrite_epd(le, lv)
        mark()
        f_dwwrite_epd(re, lv)
        mark()
    EUDEndIf()

    for epd, val in zip([le, te, re, de], [lv, tv, rv, dv]):
        f_dwwrite_epd(epd, val)

    if EUDIf()(tv < dv - 32):
        length << dv - tv
        bias << (frame * length) // FRAME_PERIOD

        f_dwwrite_epd(le, rv)
        plus(bias, length, tv, dv, te, de)

        f_dwwrite_epd(re, lv)
        f_dwwrite_epd(le, lv)
        minus(bias, length, dv, tv, te, de)
    if EUDElseIf()(tv  > dv + 32):
        length << tv - dv
        bias << (frame * length) // FRAME_PERIOD

        f_dwwrite_epd(le, rv)
        minus(bias, length, tv, dv, te, de)

        f_dwwrite_epd(re, lv)
        f_dwwrite_epd(le, lv)
        plus(bias, length, dv, tv, te, de)
    if EUDElseIf()(tv == dv):
        f_dwwrite_epd(re, lv)
        mark()

        f_dwwrite_epd(le, rv)
        f_dwwrite_epd(re, rv)
        mark()
    if EUDElse()():
        f_dwwrite_epd(re, lv)
        mark()
        f_dwwrite_epd(de, tv)
        mark()
        f_dwwrite_epd(te, dv)
        f_dwwrite_epd(de, dv)
        mark()

        f_dwwrite_epd(le, rv)
        f_dwwrite_epd(re, rv)
        mark()
        f_dwwrite_epd(te, tv)
        mark()
        f_dwwrite_epd(de, tv)
        mark()
    EUDEndIf()


    # restore location
    end_point << NextTrigger()
    for epd, val in zip([le, te, re, de], [lv, tv, rv, dv]):
        f_dwwrite_epd(epd, val)

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
        global mapw, maph
        if mapw != -1:
            dim = GetChkTokenized().getsection(b'DIM ')
            mapw = b2i2(dim, 0)
            maph = b2i2(dim, 2)
        self.location = 0
        self.centerview = 1
        self.autorefresh = 1
        self.frame = 0

        # make enable to create Scanner Sweep
        DoActions(SetMemoryX(0x661558, SetTo, 1 << 17, 1 << 17))
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
        drawRectangle(location, self.frame)

        # restore Scanner Sweep
        DoActions([
            RemoveUnit("Scanner Sweep", superuser),
            SetMemoryX(0x666458, SetTo, prev_im, 0xFFFF),
            SetMemory(0x66EFE8, SetTo, prev_is)
        ])

        self.frame += 1
        if EUDIf()(self.frame == 24):
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
        writer.write_f("Location (flags) ( %D / 256 ) // CenterView: ",
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
            strId = f_wread_epd(cur_epd + 4, 0)
            flag = f_wread_epd(cur_epd + 4, 2)

            if EUDIf()(cur == target_location):
                writer.write(0x11) # orange
            if EUDElse()():
                writer.write(0x02) # pale blue
            EUDEndIf()
            writer.write_f(" %D %H ", cur, cur_ptr)

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
            writer.write(ord(' '))
            if EUDIfNot()(strId == 0):
                writer.write_STR_string(strId)
            EUDEndIf()
            writer.write_decimal(strId)
            writer.write(ord('\n'))

            DoActions([cur_ptr.AddNumber(0x14), cur.AddNumber(1), cur_epd.AddNumber(0x14//4)])
        EUDEndInfLoop()

        writer.write(0)
