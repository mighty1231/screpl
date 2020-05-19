from eudplib import *

from ..base.eudbyterw import EUDByteRW
from ..core.appmanager import getAppManager
from ..core.appcommand import AppCommand
from .scroll import ScrollApp, LINES_PER_PAGE

LOGGER_LINE_SIZE = 216
LOGGER_LINE_COUNT = 500

# Guarantee no more than 1 Logger instance
BUF_SIZE = LOGGER_LINE_SIZE * LOGGER_LINE_COUNT
buf = Db(BUF_SIZE)
buf_start_epd = EPD(buf)
buf_end_epd = buf_start_epd + BUF_SIZE // 4

next_epd_to_write = EUDVariable(buf_start_epd)
log_index = EUDVariable()

# check whether it tracks recent logs or not
MODE_REALTIME = 0
MODE_STOPPED = 1
mode = EUDVariable(MODE_REALTIME)

writer = EUDByteRW()

multiline_buffer = Db(3000)

class MultilineLogWriter:
    def __init__(self, name):
        self.name = name
        self.writer = EUDByteRW()
        self.writer.seekepd(EPD(multiline_buffer))

    def __enter__(self):
        return self.writer

    def __exit__(self, exc_type, exc_val, exc_tb):
        reader = EUDByteRW()
        reader.seekepd(EPD(multiline_buffer))
        prev, cur = EUDCreateVariables(2)
        prev << reader.getoffset()
        cur << prev

        Logger.format("Multiline [%s]" % self.name)
        if EUDInfLoop()():
            b = reader.read()
            EUDBreakIf(b == 0)

            if EUDIf()(b == ord('\n')):
                f_bwrite(cur, 0)
                Logger.format("%S", prev, simple=True)
                prev << cur + 1
            EUDEndIf()
            cur += 1
        EUDEndInfLoop()
        Logger.format("%S", prev, simple=True)

class Logger(ScrollApp):
    @staticmethod
    def format(fmtstring, *args, simple=False):
        writer.seekepd(next_epd_to_write)
        if not simple:
            writer.write_f("\x16%D: [frame %D] ",
                log_index,
                getAppManager().getCurrentFrameNumber()
            )
        else:
            writer.write_f("\x16%D: ", log_index)
        writer.write_f(fmtstring, *args)
        writer.write(0)

        DoActions([
            next_epd_to_write.AddNumber(LOGGER_LINE_SIZE // 4),
            log_index.AddNumber(1)
        ])
        if EUDIf()(next_epd_to_write == buf_end_epd):
            next_epd_to_write << buf_start_epd
        EUDEndIf()

    @staticmethod
    def multilineWriter(name):
        return MultilineLogWriter(name)

    def onInit(self):
        ScrollApp.onInit(self)
        mode << MODE_REALTIME

    def loop(self):
        manager = getAppManager()
        if EUDIf()(mode == MODE_STOPPED):
            if EUDIf()(manager.keyPress("ESC")):
                mode << MODE_REALTIME
            if EUDElseIf()(manager.keyPress("F7")):
                self.setOffset(self.offset - LINES_PER_PAGE)
            if EUDElseIf()(manager.keyPress("F8")):
                self.setOffset(self.offset + LINES_PER_PAGE)
            EUDEndIf()
        if EUDElse()():
            if EUDIf()(manager.keyPress("ESC")):
                manager.requestDestruct()
            if EUDElseIf()(manager.keyPress("S")):
                mode << MODE_STOPPED
            if EUDElse()():
                # set offset
                if EUDIf()(log_index >= LINES_PER_PAGE):
                    self.setOffset(log_index - LINES_PER_PAGE)
                EUDEndIf()
            EUDEndIf()
        EUDEndIf()
        manager.requestUpdate()

    def writeTitle(self, writer):
        manager = getAppManager()
        if EUDIf()(mode == MODE_REALTIME):
            writer.write_f("\x16SC-REPL logs (frame=%D), Realtime View, " \
                    "press 'S' to stop view",
                manager.getCurrentFrameNumber()
            )
        if EUDElse()():
            writer.write_f("\x16SC-REPL logs (frame=%D), Stopped View, " \
                    "press 'ESC', 'F7' or 'F8'",
                manager.getCurrentFrameNumber()
            )
        EUDEndIf()

    def writeLine(self, writer, line):
        quot, rem = f_div(line, LOGGER_LINE_COUNT)
        epd = buf_start_epd + rem * (LOGGER_LINE_SIZE // 4)
        writer.write_strepd(epd)

    def getLineCount(self):
        return log_index
