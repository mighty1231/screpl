from eudplib import *
from screpl.core.appcommand import AppCommand
from screpl.core.application import Application
from screpl.encoder.const import ArgEncNumber
from screpl.main import get_app_manager
from screpl.utils.byterw import REPLByteRW

manager = get_app_manager()

_ptr = EUDVariable(0)
_size = EUDVariable(0)


DISPMODE_MAIN = 0
DISPMODE_MANUAL = 1
v_display_mode = EUDVariable()

COLOR_DEFAULT = 0x16
COLOR_BYTE = 0x08
COLOR_WORD = 0x11
COLOR_DWORD = 0x17

class MemoryApp(Application):
    fields = [
        "_ptr", "epd",
        "size",

        "cursor",
        "autorefresh"
    ]

    @staticmethod
    def set_content_ptr(ptr, size):
        _ptr << ptr
        _size << size

    @staticmethod
    def set_content_epd(epd, size):
        _ptr << ((epd * 4) + 0x58A364)
        _size << size

    def on_init(self):
        self._ptr = _ptr
        self.size = _size
        self.cursor = _ptr
        self.autorefresh = 1

        v_display_mode << DISPMODE_MAIN

        _size << 0

    def loop(self):
        if EUDIf()(manager.key_press("ESC")):
            manager.request_destruct()
        if EUDElseIf()(manager.key_down("F1")):
            v_display_mode << DISPMODE_MANUAL
            manager.request_update()
        if EUDElseIf()(manager.key_up("F1")):
            v_display_mode << DISPMODE_MAIN
            manager.request_update()
        if EUDElseIf()(manager.key_press("F7")):
            self.cursor -= 1
            manager.request_update()
        if EUDElseIf()(manager.key_press("F8")):
            self.cursor += 1
            manager.request_update()
        EUDEndIf()

        if EUDIfNot()(self.autorefresh == 0):
            manager.request_update()
        EUDEndIf()

    def print(self, writer):
        if EUDIf()(v_display_mode == DISPMODE_MAIN):
            ptr, size, cursor = self._ptr, self.size, self.cursor
            reader = REPLByteRW()

            writer.write_f(
                "%CMemoryApp (ptr = %H, cursor = %H, size = %D) "
                "Press F1 to get manual\n",
                COLOR_DEFAULT, ptr, cursor, size)

            cur_ptr, endp = EUDCreateVariables(2)
            cur_ptr << ptr
            endp << ptr + size
            reader.seekoffset(cur_ptr)

            if EUDWhileNot()(cur_ptr >= endp):
                writer.write_f("%C%H : ", COLOR_DEFAULT, cur_ptr)

                if EUDLoopN()(16):
                    EUDBreakIf(cur_ptr == endp)

                    if EUDIf()(reader.off == 0):
                        writer.write_f("%C | ", COLOR_DEFAULT)
                    if EUDElse()():
                        writer.write_f(" ")
                    EUDEndIf()

                    diff = cur_ptr - cursor
                    if EUDIf()(diff == 0):
                        writer.write(COLOR_BYTE)
                    if EUDElseIf()(diff == 1):
                        writer.write(COLOR_WORD)
                    if EUDElseIf()([diff >= 2, diff <= 3]):
                        writer.write(COLOR_DWORD)
                    if EUDElse()():
                        writer.write(COLOR_DEFAULT)
                    EUDEndIf()

                    ch = reader.read()
                    cur_ptr += 1
                    writer.write_bytehex(ch)
                EUDEndLoopN()

                writer.write(ord("\n"))
            EUDEndWhile()
        if EUDElse()():
            writer.write_f(
                "%CMemoryApp Manual\n"
                "Press F7, F8 to move %Ccursor%C\n"
                "Chat ptr(PTR) to change pointer\n"
                "Chat ptrsz(PTR, SIZE) to change pointer and size\n"
                "Chat b(BYTE) to change byte value on %Ccursor%C\n"
                "Chat w(WORD) to change word value on %Ccur%Csor%C\n"
                "Chat dw(DWORD) to change dword value on %Cc%Cur%Csor\n",
                COLOR_DEFAULT,
                COLOR_BYTE,
                COLOR_DEFAULT,
                COLOR_BYTE,
                COLOR_DEFAULT,
                COLOR_BYTE,
                COLOR_WORD,
                COLOR_DEFAULT,
                COLOR_BYTE,
                COLOR_WORD,
                COLOR_DWORD)
        EUDEndIf()
        writer.write(0)

    @AppCommand([ArgEncNumber])
    def ptr(self, ptr):
        self._ptr = ptr
        self.cursor = ptr
        manager.request_update()

    @AppCommand([ArgEncNumber, ArgEncNumber])
    def ptrsz(self, ptr, size):
        self._ptr = ptr
        self.cursor = ptr
        self.size = size
        manager.request_update()

    @AppCommand([ArgEncNumber])
    def b(self, value):
        f_bwrite(self.cursor, value)
        manager.request_update()

    @AppCommand([ArgEncNumber])
    def w(self, value):
        f_wwrite(self.cursor, value)
        manager.request_update()

    @AppCommand([ArgEncNumber])
    def dw(self, value):
        f_dwwrite(self.cursor, value)
        manager.request_update()
