from eudplib import *

from repl import Application, AppCommand

from . import appManager, locstrings, keymap, FRAME_PERIOD
from .rect import drawRectangle
from .editor import LocationEditorApp

# app-specific initializing arguments
_location = EUDVariable(1)
_result_epd = EUDVariable(0)

class LocationManagerApp(Application):
    fields = [
        "location", # 1 ~ 255
        "result_epd", # this app can make it as a result

        "frame", # parameter used on draw rectangle as animation

        "centerview", # do centerview on every setLocation() calles if 1
    ]

    @staticmethod
    def setContent(location, result_epd = None):
        # set initializing arguments
        _location << EncodeLocation(location)
        if result_epd:
            _result_epd << result_epd

    def onInit(self):
        self.location = 0
        self.centerview = 1
        self.frame = 0
        self.result_epd = _result_epd

        self.setLocation(_location)

        # restore initializing arguments
        _location << 1
        _result_epd << 0

    def setLocation(self, location):
        if EUDIf()([location >= 1, location <= 255]):
            if EUDIfNot()(location == self.location):
                self.frame = 0
                self.location = location

                if EUDIfNot()(self.centerview == 0):
                    cp = f_getcurpl()
                    f_setcurpl(appManager.superuser)
                    DoActions([CenterView(location)])
                    f_setcurpl(cp)
                EUDEndIf()
                appManager.requestUpdate()
            EUDEndIf()
        EUDEndIf()

    def onDestruct(self):
        if EUDIfNot()(self.result_epd == 0):
            f_dwwrite_epd(self.result_epd, self.location)
        EUDEndIf()

    def loop(self):
        # F7 - previous location
        # F8 - next location
        superuser = appManager.superuser

        location = self.location
        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
            EUDReturn()
        if EUDElseIf()(appManager.keyPress("F7")):
            self.setLocation(location - 1)
        if EUDElseIf()(appManager.keyPress("F8")):
            self.setLocation(location + 1)
        if EUDElseIf()(appManager.keyPress(keymap["manager"]["open_editor"])):
            LocationEditorApp.setTarget(location)
            appManager.startApplication(LocationEditorApp)
            EUDReturn()
        EUDEndIf()

        # backup "Scanner Sweep" and prepare effect
        # thanks to Artanis(kein0011@naver.com),
        #   - https://cafe.naver.com/edac/77656
        # sprites[380] is "Scanner Sweep Hit"
        # image[232] is "Nuke Beam"
        # sprites[380].image <- 232
        # images[232].iscript <- 250
        prev_im = f_dwread_epd(EPD(0x666160 + 2*380))
        prev_is = f_dwread_epd(EPD(0x66EC48 + 4*232))
        DoActions([
            SetMemoryX(0x666160 + 2*380, SetTo, 232, 0xFFFF),
            SetMemory(0x66EC48 + 4*232, SetTo, 250)
        ])

        # draw location with "Scanner Sweep"
        drawRectangle(self.location, self.frame, FRAME_PERIOD)

        # restore "Scanner Sweep"
        DoActions([
            RemoveUnit("Scanner Sweep", superuser),
            SetMemoryX(0x666160 + 2*380, SetTo, prev_im, 0xFFFF),
            SetMemory(0x66EC48 + 4*232, SetTo, prev_is)
        ])

        self.frame += 1
        if EUDIf()(self.frame == FRAME_PERIOD):
            self.frame = 0
        EUDEndIf()
        appManager.requestUpdate()

    @AppCommand([])
    def cv(self):
        '''
        Toggle CenterView Effect
        '''
        if EUDIfNot()(self.centerview == 0):
            self.centerview = 0
        if EUDElse()():
            self.centerview = 1
        EUDEndIf()
        appManager.requestUpdate()

    def print(self, writer):
        writer.write_f("\x16Location (sizeX, sizeY, flags) ( %D / 255 ) // CenterView: ",
                self.location)
        if EUDIfNot()(self.centerview == 0):
            writer.write_f("\x07ON\n")
        if EUDElse()():
            writer.write_f("\x08OFF\n")
        EUDEndIf()

        target_location = self.location

        quot, mod = f_div(target_location - 1, 8)
        cur = quot * 8 + 1
        until = cur + 8
        if EUDIf()(until == 255):
            until << 254
        EUDEndIf()

        # fill contents
        cur_epd = EPD(0x58DC60 - 0x14) + (0x14 // 4) * cur
        cur_ptr = (0x58DC60 - 0x14) + 0x14 * cur
        if EUDInfLoop()():
            EUDBreakIf(cur >= until)

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
            bottom  = f_dwread_epd(cur_epd + 3)
            flag = f_wread_epd(cur_epd + 4, 2)

            if EUDIf()(cur == target_location):
                writer.write(0x11) # orange
            if EUDElse()():
                writer.write(0x02) # pale blue
            EUDEndIf()

            str_epd = locstrings[cur]
            if EUDIfNot()(str_epd == 0):
                writer.write_f(" %D '%E': %D x %D // ", cur, str_epd, right-left, bottom-top)
            if EUDElse()():
                writer.write_f(" %D: %D x %D // ", cur, right-left, bottom-top)
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
