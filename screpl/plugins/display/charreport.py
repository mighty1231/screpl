from eudplib import *

from screpl.core.application import Application
from screpl.main import get_app_manager
from screpl.main import get_main_writer
from screpl.utils.debug import DisplayWriter
from screpl.utils.conststring import EPDConstString

from . import eval_screen_size

storage = Db(20000)
v_remaining_bytes = EUDVariable(0)
v_written = EUDVariable(0)

app_manager = get_app_manager()

test_strings = [chr(t) for t in range(0x21, 0x7F)]
test_strings.append(b"\xea\xb0\x80") # Korean character
test_dbs = EUDArray(list(map(EPDConstString, test_strings)))

def _write_report():
    """fill in 'storage' with report

    Each characters and its maximum count for single line"""
    writer = get_main_writer()
    writer.seekepd(EPD(storage))

    screen_x, _ = eval_screen_size()
    writer.write_f("[char report width = %D]\n", screen_x)

    # display and check change of display index
    v_index = EUDVariable()
    v_count = EUDVariable()
    v_num_lines = EUDVariable()
    db_cur = EUDVariable()

    v_index << 0
    v_count << 1
    db_cur << test_dbs[0]
    if EUDInfLoop()():
        EUDBreakIf(v_index >= len(test_strings))

        # print char 'v_index' v_count times
        v_disp_index = f_dwread_epd(EPD(0x640B58))
        with DisplayWriter(preserve_chat=False) as dispwriter:
            i = EUDVariable()
            i << 0
            if EUDInfLoop()():
                EUDBreakIf(i >= v_count)
                dispwriter.write_f("%E", db_cur)
                i += 1
            EUDEndInfLoop()
            dispwriter.write(0)

        v_num_lines << f_dwread_epd(EPD(0x640B58)) - v_disp_index
        if EUDIf()(v_num_lines.ExactlyX(0x80000000, 0x80000000)):
            v_num_lines += 11
        EUDEndIf()

        if EUDIf()(v_num_lines <= 1):
            v_count += 1
            if EUDIf()(v_count == 400):
                writer.write_f("%E: Unknown\n", db_cur)
                v_count << 1
                v_index += 1
                db_cur << test_dbs[v_index]
            EUDEndIf()
        if EUDElse()():
            writer.write_f("%E: %D\n", db_cur, v_count-1)
            v_count << 1
            v_index += 1
            db_cur << test_dbs[v_index]
        EUDEndIf()

        # restore chat
        SeqCompute([(EPD(0x640B58), SetTo, v_disp_index)])
    EUDEndInfLoop()

    writer.write(0)
    v_written << 0
    v_remaining_bytes << (writer.getoffset() - storage)

class CharReportApp(Application):
    """Character count report to bridge client"""

    def on_init(self):
        _write_report()

    def loop(self):
        global v_written, v_remaining_bytes

        v_new_written = app_manager.send_app_output_to_bridge(
            storage + v_written,
            v_remaining_bytes)

        v_remaining_bytes -= v_new_written
        v_written += v_new_written
        if EUDIf()(v_remaining_bytes == 0):
            app_manager.request_destruct()
        EUDEndIf()
        app_manager.request_update()

    def print(self, writer):
        writer.write_f("\x16Character report - bridge client is required\n")
        writer.write_f("\x13Sent %D bytes / Remaining %D bytes\n\n\n\n",
            v_written,
            v_remaining_bytes
        )
        writer.write(0)
