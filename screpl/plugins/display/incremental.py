from eudplib import *

from screpl.core.application import Application
from screpl.main import get_app_manager
from screpl.utils.conststring import EPDConstString
from screpl.utils.debug import DisplayWriter

from . import eval_screen_size

db_char = Db(b'a' + b'\x00'*200)
v_count = EUDVariable()
v_num_lines = EUDVariable()
v_screen_size_x = EUDVariable()
v_screen_size_y = EUDVariable()

app_manager = get_app_manager()

class IncrementalDisplayApp(Application):
    def on_chat(self, address):
        """read chat, fill db, and reset"""
        f_strcpy(db_char, address)
        v_count << 1
        v_num_lines << 1

    def loop(self):
        global db_char, v_num_lines, v_count
        if EUDIf()(app_manager.key_press("ESC")):
            app_manager.request_destruct()
        EUDEndIf()
        app_manager.request_update()

        # update screen size and check
        sizes = eval_screen_size()
        if EUDIfNot()(v_screen_size_x == sizes[0]):
            v_screen_size_x << sizes[0]
            v_count << 1
            v_num_lines << 1
        EUDEndIf()
        if EUDIfNot()(v_screen_size_y == sizes[1]):
            v_screen_size_y << sizes[1]
            v_count << 1
            v_num_lines << 1
        EUDEndIf()

        # found count
        if EUDIf()(v_num_lines == 2):
            EUDReturn()
        EUDEndIf()

        # display and check change of display index
        v_disp_index = f_dwread_epd(EPD(0x640B58))
        with DisplayWriter(preserve_chat=False) as writer:
            i = EUDVariable()
            i << 0
            if EUDInfLoop()():
                EUDBreakIf(i >= v_count)
                writer.write_f("%E", EPD(db_char))
                i += 1
            EUDEndInfLoop()
            writer.write(0)

        v_num_lines << f_dwread_epd(EPD(0x640B58)) - v_disp_index
        if EUDIf()(v_num_lines.ExactlyX(0x80000000, 0x80000000)):
            v_num_lines += 11
        EUDEndIf()

        # for next operation...
        if EUDIf()(v_num_lines <= 1):
            v_count += 1
        EUDEndIf()

        # restore chat
        SeqCompute([(EPD(0x640B58), SetTo, v_disp_index)])

    def print(self, writer):
        global db_char, v_num_lines, v_count
        v_max_cnt = v_count - 1
        writer.write_f("Display ch='%E' ln=%D cnt=%D mouse_xy=(%D, %D) screensize_xy=(%D, %D)\n",
                       EPD(db_char),
                       v_num_lines,
                       v_max_cnt,
                       f_dwread_epd(EPD(0x006CDDC4)),
                       f_dwread_epd(EPD(0x006CDDC8)),
                       v_screen_size_x,
                       v_screen_size_y,
                       )
        i = EUDVariable()
        i << 0
        if EUDInfLoop()():
            EUDBreakIf(i >= v_max_cnt)
            writer.write_f("%E", EPD(db_char))
            i += 1
        EUDEndInfLoop()
        writer.write(ord("\n"))
        writer.write_strepd(EPDConstString(b"\xe2\x96\xa0 2\n"))
        writer.write_strepd(EPDConstString(b"\xe2\x96\xa0 3\n"))
        writer.write_strepd(EPDConstString(b"\xe2\x96\xa0 4\n"))
        writer.write_strepd(EPDConstString(b"\xe2\x96\xa0 5\n"))
        writer.write_strepd(EPDConstString(b"\xe2\x96\xa0 6\n"))
        writer.write_strepd(EPDConstString(b"\xe2\x96\xa0 7\n"))
        writer.write_strepd(EPDConstString(b"\xe2\x96\xa0 8\n"))
        writer.write_strepd(EPDConstString(b"\xe2\x96\xa0 9\n"))
        writer.write_strepd(EPDConstString(b"\xe2\x96\xa0 10\n"))
        writer.write(0)
