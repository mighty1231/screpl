from eudplib import *

from screpl.core.application import Application
from screpl.utils.byterw import REPLByteRW

from screpl.main import get_app_manager, get_main_writer

app_manager = get_app_manager()

storage = Db(200000)
remaining_bytes = EUDVariable(0)
written = EUDVariable(0)

writer = get_main_writer()

_ptr = EUDVariable()
_size = EUDVariable()

def dump_to_storage():
    global writer
    writer.seekepd(EPD(storage))
    reader = REPLByteRW()

    reader.seekoffset(_ptr)
    if EUDInfLoop()():
        EUDBreakIf(_size == 0)

        b = reader.read()
        writer.write_bytehex(b)
        DoActions(_size.SubtractNumber(1))
    EUDEndInfLoop()

    writer.write(ord('\n'))
    writer.write(0)

    written << 0
    remaining_bytes << (writer.getoffset() - storage)

class DumpApp(Application):
    @staticmethod
    def set_target(ptr, size):
        _ptr << ptr
        _size << size

    def on_init(self):
        dump_to_storage()

    def loop(self):
        global written, remaining_bytes

        if EUDIf()(app_manager.key_press("ESC")):
            app_manager.request_destruct()
        EUDEndIf()

        new_written = app_manager.send_app_output_to_bridge(storage + written, remaining_bytes)

        remaining_bytes -= new_written
        written += new_written
        if EUDIf()(app_manager.synchronize([
                (EPD(remaining_bytes.getValueAddr()), Exactly, 0)])):
            app_manager.request_destruct()
        EUDEndIf()
        app_manager.request_update()

    def print(self, writer):
        writer.write_f("\x13Memory Dumping...\n")
        writer.write_f("\x13Sent %D bytes / Remaining %D bytes\n\n\n\n", written, remaining_bytes)
        writer.write(0)
