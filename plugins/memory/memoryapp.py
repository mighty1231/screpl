from eudplib import *
from repl import (
    Application,
    AppCommand,
    get_app_manager,
    ArgEncNumber
)

manager = get_app_manager()

_ptr = EUDVariable(0)
_epd = EUDVariable(0)
_size = EUDVariable(0)

class MemoryApp(Application):
    fields = [
        "ptr", "epd",

        "size", 
        "autorefresh"
    ]

    @staticmethod
    def setContent_ptr(ptr, size):
        _ptr << ptr
        _epd << EPD(ptr)
        _size << size

    @staticmethod
    def setContent_epd(epd, size):
        _ptr << ((epd * 4) + 0x58A364)
        _epd << epd
        _size << size

    def onInit(self):
        self.ptr = _ptr
        self.epd = _epd
        self.size = _size
        self.autorefresh = 1

        _size << 0

    def loop(self):
        if EUDIf()(manager.keyPress("ESC")):
            manager.requestDestruct()
            EUDReturn()
        EUDEndIf()
        if EUDIfNot()(self.autorefresh == 0):
            manager.requestUpdate()
        EUDEndIf()

    def print(self, writer):
        ptr, epd, size = self.ptr, self.epd, self.size

        writer.write_f("Memory (ptr = %H, epd = %D, size = %D)\n",
            ptr, epd, size)

        cur_ptr, endp = EUDCreateVariables(2)
        cur_ptr << ptr
        endp << ptr + size

        if EUDWhileNot()(cur_ptr >= endp):
            writer.write_f("%H :  ", cur_ptr)
            writer.write_memoryTable(cur_ptr, 4)
            cur_ptr += 4

            for _ in range(3):
                EUDBreakIf(cur_ptr >= endp)
                writer.write_f(" | ")
                writer.write_memoryTable(cur_ptr, 4)
                cur_ptr += 4
            writer.write(ord("\n"))
        EUDEndWhile()
        writer.write(0)

    @AppCommand([ArgEncNumber])
    def setptr(self, ptr):
        self.ptr = ptr
        self.epd = EPD(ptr)
        manager.requestUpdate()

    @AppCommand([ArgEncNumber, ArgEncNumber])
    def setptrsz(self, ptr, size):
        self.ptr = ptr
        self.epd = EPD(ptr)
        self.size = size
        manager.requestUpdate()
