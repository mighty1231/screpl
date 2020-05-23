from eudplib import *

import screpl.core.application as application
import screpl.core.appmethod as appmethod
import screpl.main as main
import screpl.utils.conststring as conststring

LINES_PER_PAGE = 8

class ScrollApp(application.Application):
    fields = [
        "offset", # top line number
    ]

    def onInit(self):
        self.offset = 0

    @appmethod.AppTypedMethod([], [], getWriterAsParam=True)
    def writeTitle(self, writer):
        ''' OVERRIDE THIS METHOD '''
        writer.write_strepd(conststring.EPDConstString("Default Scroll App"))

    @appmethod.AppTypedMethod([None], [], getWriterAsParam=True)
    def writeLine(self, writer, line):
        ''' OVERRIDE THIS METHOD '''
        pass

    @appmethod.AppTypedMethod([], [None])
    def getLineCount(self):
        ''' OVERRIDE THIS METHOD '''
        return 0

    def setOffset(self, new_offset):
        offset, linecount = self.offset, self.getLineCount()
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
        if EUDIf()(manager.keyPress("ESC")):
            manager.requestDestruct()
        if EUDElseIf()(manager.keyPress("F7")):
            self.setOffset(self.offset - LINES_PER_PAGE)
        if EUDElseIf()(manager.keyPress("F8")):
            self.setOffset(self.offset + LINES_PER_PAGE)
        EUDEndIf()

        # always update
        manager.requestUpdate()

    def print(self, writer):
        # title
        self.writeTitle()
        writer.write(ord('\n'))

        offset, linecount = self.offset, self.getLineCount()

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
            self.writeLine(cur)
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
