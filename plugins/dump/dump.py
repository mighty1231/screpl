from eudplib import *
from repl import Application, EUDByteRW

from . import appManager

storage = Db(200000)
remaining_bytes = EUDVariable(0)
written = EUDVariable(0)

writer = appManager.getWriter()

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

        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
            EUDReturn()
        EUDEndIf()

        new_written = appManager.exportAppOutputToBridge(storage + written, remaining_bytes)

        remaining_bytes -= new_written
        written += new_written
        if EUDIf()(remaining_bytes == 0):
            appManager.requestDestruct()
        EUDEndIf()
        appManager.requestUpdate()

    def print(self, writer):
        writer.write_f("\x13Memory Dumping...\n")
        writer.write_f("\x13Sent %D bytes / Remaining %D bytes\n\n\n\n", written, remaining_bytes)
        writer.write(0)