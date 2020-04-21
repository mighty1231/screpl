from eudplib import *

from .application import Application
from .appmanager import getAppManager
from .eudbyterw import EUDByteRW

import functools

PAGE_NUMLINES = 8
LINE_SIZE = 216
LOGGER_SIZE = 10

# Guarantee no more than 1 Logger instance
BUF_SIZE = LINE_SIZE * LOGGER_SIZE
buf = Db(BUF_SIZE)
buf_start_epd = EPD(buf)
buf_end_epd = buf_start_epd + BUF_SIZE // 4
buf_epd_var = EUDVariable(buf_start_epd)
log_index = EUDVariable()

writer = EUDByteRW()

class Logger(Application):
    @staticmethod
    def format(fmtstring, *args):
        writer.seekepd(buf_epd_var)
        writer.write_f("%D: [frame %D] ",
            log_index,
            getAppManager().getCurrentFrameNumber()
        )
        writer.write_f(fmtstring, *args)
        writer.write(0)

        DoActions([
            buf_epd_var.AddNumber(LINE_SIZE // 4),
            log_index.AddNumber(1)
        ])
        if EUDIf()(buf_epd_var == buf_end_epd):
            buf_epd_var << buf_start_epd
        EUDEndIf()

    def onChat(self, offset):
        pass

    def loop(self):
        manager = getAppManager()
        if EUDIf()(manager.keyPress("ESC")):
            manager.requestDestruct()
        EUDEndIf()
        manager.requestUpdate()

    def print(self, writer):
        manager = getAppManager()
        writer.write_f("\x16SC-REPL logs (frame=%D)\n",
            manager.getCurrentFrameNumber()
        )

        cur, until, pageend = EUDCreateVariables(3)
        if EUDIf()(log_index <= PAGE_NUMLINES): # log size <= 8
            # fill logs
            cur << buf_start_epd
            until << buf_start_epd + log_index * (LINE_SIZE // 4)
            pageend << buf_start_epd + PAGE_NUMLINES * (LINE_SIZE // 4)
            if EUDInfLoop()():
                EUDBreakIf(cur >= until)
                writer.write_strepd(cur)
                writer.write(ord('\n'))
                DoActions(cur.AddNumber(LINE_SIZE // 4))
            EUDEndInfLoop()

            # make empty lines
            if EUDInfLoop()():
                EUDBreakIf(cur >= pageend)
                writer.write(ord('\n'))
                DoActions(cur.AddNumber(LINE_SIZE // 4))
            EUDEndInfLoop()
            writer.write(0)
        if EUDElse()():
            cur << buf_epd_var - PAGE_NUMLINES * (LINE_SIZE // 4)
            pageend << buf_epd_var
            if EUDIfNot()(cur >= buf_start_epd):
                cur += BUF_SIZE // 4
            EUDEndIf()
            if EUDInfLoop()():
                EUDBreakIf(cur == pageend)
                writer.write_strepd(cur)
                writer.write(ord('\n'))
                DoActions(cur.AddNumber(LINE_SIZE // 4))
                if EUDIf()(cur == buf_end_epd):
                    cur << buf_start_epd
                EUDEndIf()
            EUDEndInfLoop()
            writer.write(0)
        EUDEndIf()
