from eudplib import *

from ..core.app import Application, getAppManager
from ..utils import EPDConstString, EPDConstStringArray

_title_epd = EUDVariable(EPDConstString("Title"))
_epdarray = EUDVariable(EPDConstString("Hello World!"))
_linecount = EUDVariable(1)

class StaticApp(Application):
    fields = [
        "title_epd",

        "linecount",
        "content_epd",

        "lines_per_page",
        "offset", # line number
    ]

    @staticmethod
    def setContent(title, content):
        _title_epd << EPDConstString(title)
        epdarray, linecount = EPDConstStringArray(content)
        _epdarray << EPD(epdarray)
        _linecount << linecount

    def init(self):
        self.title_epd = _title_epd
        self.linecount = _linecount
        self.content_epd = _epdarray
        self.lines_per_page = 8
        self.offset = 0

    def setOffset(self, new_offset):
        prevoffset, linecount, lpp = self.offset, self.linecount, self.lines_per_page
        if EUDIf()([new_offset <= 0x80000000, linecount > lpp]):
            if EUDIfNot()(new_offset >= linecount - lpp):
                self.offset = new_offset
            if EUDElse()():
                self.offset = linecount - lpp
            EUDEndIf()
        if EUDElse()():
            self.offset = 0
        EUDEndIf()

        if EUDIfNot()(prevoffset == self.offset):
            getAppManager().requestUpdate()
        EUDEndIf()

    def loop(self):
        # F7 - previous page
        # F8 - next page
        manager = getAppManager()
        if EUDIf()(manager.keyPress("ESC")):
            manager.requestDestruct()
        if EUDElseIf()(manager.keyPress("F7")):
            self.setOffset(self.offset - self.lines_per_page)
        if EUDElseIf()(manager.keyPress("F8")):
            self.setOffset(self.offset + self.lines_per_page)
        EUDEndIf()

    def print(self, writer):
        # title
        writer.write_f("%E ( %D / %D )\n",
                self.title_epd, self.offset, self.linecount)

        cur, pageend, until = EUDCreateVariables(3)
        cur << self.offset
        pageend << self.offset + self.lines_per_page
        if EUDIf()(pageend >= self.linecount):
            until << self.linecount
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

        # fill with empty lines
        if EUDInfLoop()():
            EUDBreakIf(cur >= pageend)
            writer.write(ord('\n'))
            DoActions(cur.AddNumber(1))
        EUDEndInfLoop()
        writer.write(0)