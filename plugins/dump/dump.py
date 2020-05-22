from eudplib import *

from repl.core.application import Application
from repl.utils.eudbyterw import EUDByteRW

from . import app_manager

storage = Db(200000)
remaining_bytes = EUDVariable(0)
written = EUDVariable(0)

writer = app_manager.getWriter()

_ptr = EUDVariable()
_size = EUDVariable()

def dumpToStorage():
    global writer
    writer.seekepd(EPD(storage))
    reader = EUDByteRW()

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
    def setTarget(ptr, size):
        _ptr << ptr
        _size << size

    def onInit(self):
        dumpToStorage()

    def loop(self):
        global written, remaining_bytes

        if EUDIf()(app_manager.keyPress("ESC")):
            app_manager.requestDestruct()
            EUDReturn()
        EUDEndIf()

        new_written = app_manager.exportAppOutputToBridge(storage + written, remaining_bytes)

        remaining_bytes -= new_written
        written += new_written
        if EUDIf()(remaining_bytes == 0):
            app_manager.requestDestruct()
        EUDEndIf()
        app_manager.requestUpdate()

    def print(self, writer):
        writer.write_f("\x13Memory Dumping...\n")
        writer.write_f("\x13Sent %D bytes / Remaining %D bytes\n\n\n\n", written, remaining_bytes)
        writer.write(0)
