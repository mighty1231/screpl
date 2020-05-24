
from eudplib import *

import screpl.utils.byterw as rw
import screpl.main as main

from . import scroll

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

writer = rw.REPLByteRW()

multiline_buffer = Db(3000)

class MultilineLogWriter:
    def __init__(self, title):
        self.title = title
        self.writer = rw.REPLByteRW()
        self.writer.seekepd(EPD(multiline_buffer))

    def __enter__(self):
        return self.writer

    def __exit__(self, exc_type, exc_val, exc_tb):
        reader = rw.REPLByteRW()
        reader.seekepd(EPD(multiline_buffer))
        prev, cur = EUDCreateVariables(2)
        prev << reader.getoffset()
        cur << prev

        Logger.format("Multi-line log [%s]" % self.title)
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

class Logger(scroll.ScrollApp):
    @staticmethod
    def format(fmtstring, *args, simple=False):
        writer.seekepd(next_epd_to_write)
        if not simple:
            writer.write_f("\x16%D: [frame %D] ",
                           log_index,
                           main.get_app_manager().get_current_frame_number())
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
    def multiline_log_writer(title):
        """Supports to log several lines

        Usage

        .. code-block: python

            with Logger.multiline_log_writer("log_title") as writer:
                writer.write_f("Hello!\n")
                writer.write_f("World!\n")
                writer.write(0)
        """
        return MultilineLogWriter(title)

    def on_init(self):
        scroll.ScrollApp.on_init(self)
        mode << MODE_REALTIME

    def loop(self):
        manager = main.get_app_manager()
        if EUDIf()(mode == MODE_STOPPED):
            if EUDIf()(manager.key_press("ESC")):
                mode << MODE_REALTIME
            if EUDElseIf()(manager.key_press("F7")):
                self.set_offset(self.offset - scroll.LINES_PER_PAGE)
            if EUDElseIf()(manager.key_press("F8")):
                self.set_offset(self.offset + scroll.LINES_PER_PAGE)
            EUDEndIf()
        if EUDElse()():
            if EUDIf()(manager.key_press("ESC")):
                manager.request_destruct()
            if EUDElseIf()(manager.key_press("S")):
                mode << MODE_STOPPED
            if EUDElse()():
                # set offset
                if EUDIf()(log_index >= scroll.LINES_PER_PAGE):
                    self.set_offset(log_index - scroll.LINES_PER_PAGE)
                EUDEndIf()
            EUDEndIf()
        EUDEndIf()
        manager.request_update()

    def write_title(self, writer):
        manager = main.get_app_manager()
        if EUDIf()(mode == MODE_REALTIME):
            writer.write_f("\x16SC-REPL logs (frame=%D), Realtime View, "
                           "press 'S' to stop view",
                           manager.get_current_frame_number())
        if EUDElse()():
            writer.write_f("\x16SC-REPL logs (frame=%D), Stopped View, "
                           "press 'ESC', 'F7' or 'F8'",
                           manager.get_current_frame_number())
        EUDEndIf()

    def write_line(self, writer, line):
        quot, rem = f_div(line, LOGGER_LINE_COUNT)
        epd = buf_start_epd + rem * (LOGGER_LINE_SIZE // 4)
        writer.write_strepd(epd)

    def get_line_count(self):
        return log_index
