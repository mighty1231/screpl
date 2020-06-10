from eudplib import *

import screpl.core.application as application
import screpl.utils.conststring as cs
import screpl.main as main

_title_epd = EUDVariable(cs.EPDConstString("Title"))
_epdarray = EUDVariable(cs.EPDConstString("Hello World!"))
_linecount = EUDVariable(1)

class StaticApp(application.Application):
    fields = [
        "title_epd",

        "linecount",
        "content_epd",

        "lines_per_page",
        "offset", # line number
    ]

    @staticmethod
    def set_content(title, content):
        _title_epd << cs.EPDConstString(title)
        epdarray, linecount = cs.EPDConstStringArray(content)
        _epdarray << EPD(epdarray)
        _linecount << linecount

    def on_init(self):
        self.title_epd = _title_epd
        self.linecount = _linecount
        self.content_epd = _epdarray
        self.lines_per_page = 8
        self.offset = 0

    def set_offset(self, new_offset):
        prev_offset, linecount, lpp = self.offset, self.linecount, self.lines_per_page
        if EUDIf()([new_offset <= 0x80000000, linecount > lpp]):
            if EUDIfNot()(new_offset >= linecount - lpp):
                self.offset = new_offset
            if EUDElse()():
                self.offset = linecount - lpp
            EUDEndIf()
        if EUDElse()():
            self.offset = 0
        EUDEndIf()

        if EUDIfNot()(prev_offset == self.offset):
            main.get_app_manager().request_update()
        EUDEndIf()

    def loop(self):
        # F7 - previous page
        # F8 - next page
        manager = main.get_app_manager()
        if EUDIf()(manager.key_press("ESC")):
            manager.request_destruct()
        if EUDElseIf()(manager.key_press("F7")):
            self.set_offset(self.offset - self.lines_per_page)
        if EUDElseIf()(manager.key_press("F8")):
            self.set_offset(self.offset + self.lines_per_page)
        EUDEndIf()

    def print(self, writer):
        # title
        offset, linecount = self.offset, self.linecount
        writer.write_f("%E ( %D / %D )\n",
                self.title_epd, offset, linecount)

        cur, pageend, until = EUDCreateVariables(3)
        cur << self.offset
        pageend << self.offset + self.lines_per_page
        if EUDIf()(pageend >= linecount):
            until << linecount
        if EUDElse()():
            until << pageend
        EUDEndIf()

        # fill with contents
        if EUDInfLoop()():
            EUDBreakIf(cur >= until)
            writer.write_strepd(f_dwread_epd(self.content_epd + cur))
            writer.write(ord('\n'))

            DoActions(cur.AddNumber(1))
        EUDEndInfLoop()

        writer.write(0)
