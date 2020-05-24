from eudplib import *

import screpl.core.application as application
import screpl.core.appmethod as appmethod
import screpl.main as main
import screpl.utils.conststring as conststring
import screpl.utils.debug as debug

LINES_PER_PAGE = 8

class ScrollApp(application.Application):
    fields = [
        "offset", # top line number
    ]

    def on_init(self):
        self.offset = 0

    @appmethod.AppTypedMethod([], [], with_main_writer=True)
    def write_title(self, writer):
        ''' OVERRIDE THIS METHOD '''
        debug.f_raise_error("NotImplementedError: ScrollApp.write_title")

    @appmethod.AppTypedMethod([None], [], with_main_writer=True)
    def write_line(self, writer, line):
        ''' OVERRIDE THIS METHOD '''
        debug.f_raise_error("NotImplementedError: ScrollApp.write_line")

    @appmethod.AppTypedMethod([], [None])
    def get_line_count(self):
        ''' OVERRIDE THIS METHOD '''
        debug.f_raise_error("NotImplementedError: ScrollApp.get_line_count")

    def set_offset(self, new_offset):
        offset, linecount = self.offset, self.get_line_count()
        if EUDIf()([new_offset <= 0x80000000, linecount >= LINES_PER_PAGE+1]):
            if EUDIfNot()(new_offset >= linecount - LINES_PER_PAGE):
                self.offset = new_offset
            if EUDElse()():
                self.offset = linecount - LINES_PER_PAGE
            EUDEndIf()
        if EUDElse()():
            self.offset = 0
        EUDEndIf()

    def loop(self):
        # F7 - previous page
        # F8 - next page
        manager = main.get_app_manager()
        if EUDIf()(manager.key_press("ESC")):
            manager.request_destruct()
        if EUDElseIf()(manager.key_press("F7")):
            self.set_offset(self.offset - LINES_PER_PAGE)
        if EUDElseIf()(manager.key_press("F8")):
            self.set_offset(self.offset + LINES_PER_PAGE)
        EUDEndIf()

        # always update
        manager.request_update()

    def print(self, writer):
        # title
        self.write_title()
        writer.write(ord('\n'))

        offset, linecount = self.offset, self.get_line_count()

        cur, pageend, until = EUDCreateVariables(3)
        cur << offset
        pageend << offset + LINES_PER_PAGE
        if EUDIf()(pageend >= linecount):
            until << linecount
        if EUDElse()():
            until << pageend
        EUDEndIf()

        # fill with contents
        if EUDInfLoop()():
            EUDBreakIf(cur >= until)
            self.write_line(cur)
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
