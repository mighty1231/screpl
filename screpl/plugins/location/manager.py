from eudplib import *

from screpl.core.appcommand import AppCommand
from screpl.core.application import Application
from screpl.resources.table.tables import get_locationname_epd

from . import app_manager, keymap, FRAME_PERIOD
from .rect import draw_rectangle
from .editor import LocationEditorApp

# app-specific initializing arguments
_location = EUDVariable(1)
_resultref_location_epd = EUDVariable(EPD(0))

class LocationManagerApp(Application):
    fields = [
        "location", # 1 ~ 255
        "resultref_location_epd", # this app can make a result

        "frame", # parameter used on draw rectangle as animation

        "centerview", # do centerview on every set_location() calles if 1
    ]

    @staticmethod
    def set_content(location, resultref_location_epd = None):
        # set initializing arguments
        _location << EncodeLocation(location)
        if resultref_location_epd:
            _resultref_location_epd << resultref_location_epd

    def on_init(self):
        self.location = 0
        self.centerview = 1
        self.frame = 0
        self.resultref_location_epd = _resultref_location_epd

        self.set_location(_location)

        # restore initializing arguments
        _location << 1
        _resultref_location_epd << EPD(0)

    def set_location(self, new_location):
        Trigger(
            conditions = new_location.AtLeast(0x80000000),
            actions = new_location.SetNumber(1)
        )
        Trigger(
            conditions = new_location.Exactly(0),
            actions = new_location.SetNumber(1)
        )
        Trigger(
            conditions = new_location.AtLeast(256),
            actions = new_location.SetNumber(255)
        )
        if EUDIfNot()(new_location == self.location):
            self.frame = 0
            self.location = new_location

            if EUDIfNot()(self.centerview == 0):
                cp = f_getcurpl()
                f_setcurpl(app_manager.get_superuser_id())
                DoActions([CenterView(new_location)])
                f_setcurpl(cp)
            EUDEndIf()
            app_manager.request_update()
        EUDEndIf()

    def on_destruct(self):
        resultref_location_epd = self.resultref_location_epd
        if EUDIfNot()(resultref_location_epd == EPD(0)):
            f_dwwrite_epd(resultref_location_epd, self.location)
        EUDEndIf()

    def loop(self):
        # F7 - previous location
        # F8 - next location
        location = self.location
        if EUDIf()(app_manager.key_press("ESC")):
            app_manager.request_destruct()
            EUDReturn()
        if EUDElseIf()(app_manager.key_press("F7", hold=["LCTRL"])):
            self.set_location(location - 8)
        if EUDElseIf()(app_manager.key_press("F7")):
            self.set_location(location - 1)
        if EUDElseIf()(app_manager.key_press("F8", hold=["LCTRL"])):
            self.set_location(location + 8)
        if EUDElseIf()(app_manager.key_press("F8")):
            self.set_location(location + 1)
        if EUDElseIf()(app_manager.key_press(keymap["manager"]["open_editor"])):
            LocationEditorApp.set_target(location)
            app_manager.start_application(LocationEditorApp)
            EUDReturn()
        EUDEndIf()

        # draw location with "Scanner Sweep"
        draw_rectangle(self.location, self.frame, FRAME_PERIOD)

        frame = self.frame + 1
        Trigger(
            conditions = frame.Exactly(FRAME_PERIOD),
            actions = frame.SetNumber(0)
        )
        self.frame = frame
        app_manager.request_update()

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
        app_manager.request_update()

    def print(self, writer):
        writer.write_f("\x16Location (sizeX, sizeY, flags) F7,F8 to navigate // press '{}' to edit " \
            "// CenterView: ".format(keymap["manager"]["open_editor"]))
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

            str_epd = get_locationname_epd(cur)
            writer.write_f(" %D %E: %D x %D // ", cur, str_epd, right-left, bottom-top)

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
