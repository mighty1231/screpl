from eudplib import *
from repl import (
    Application,
    AppTypedMethod,
    AppCommand,
    argEncNumber
)

from . import *

MODE_CONFIG    = 0
MODE_EXPORTING = 1
v_mode = EUDVariable(MODE_CONFIG)

storage = Db(STRING_BUFFER_SZ)
remaining_bytes = EUDVariable(0)
written = EUDVariable(0)

def writeStrings():
    global string_buffer, new_alloc_epd
    writer = appManager.getWriter()
    writer.seekepd(EPD(storage))

    cur_epd = EUDVariable()
    cur_epd << EPD(string_buffer)

    if EUDInfLoop()():
        EUDBreakIf(cur_epd == new_alloc_epd)

        if EUDIf()(MemoryXEPD(cur_epd, Exactly, 0x0D0D0D, 0xFFFFFF)):
            b = f_bread_epd(cur_epd, 3)
            if EUDIf()(b <= 0x1F):
                if EUDIf()([b >= 9, b <= 10]): # \t and \n
                    writer.write(b)
                if EUDElse()():
                    writer.write(ord('<'))
                    writer.write_bytehex(b)
                    writer.write(ord('>'))
                EUDEndIf()
            if EUDElse()():
                writer.write(b)
            EUDEndIf()
        if EUDElseIf()(MemoryXEPD(cur_epd, Exactly, 0x0D0D, 0xFFFF)):
            b1 = f_bread_epd(cur_epd, 2)
            b2 = f_bread_epd(cur_epd, 3)
            writer.write(b1)
            writer.write(b2)
        if EUDElseIf()(MemoryXEPD(cur_epd, Exactly, 0x0D, 0xFF)):
            b1 = f_bread_epd(cur_epd, 1)
            b2 = f_bread_epd(cur_epd, 2)
            b3 = f_bread_epd(cur_epd, 3)
            writer.write(b1)
            writer.write(b2)
            writer.write(b3)
        if EUDElse()():
            # null-end
            writer.write_f("\n//------------//\n")
            if EUDInfLoop()():
                EUDBreakIf(cur_epd == new_alloc_epd)
                EUDBreakIf(MemoryEPD(cur_epd, AtLeast, 1))
                cur_epd += 1
            EUDEndInfLoop()
            EUDContinue()
        EUDEndIf()

        cur_epd += 1
    EUDEndInfLoop()
    writer.write(0)

    written << 0
    remaining_bytes << (writer.getoffset() - storage)

class StringExporterApp(Application):
    def onInit(self):
        pass

    def onDestruct(self):
        pass

    def loop(self):
        global written, remaining_bytes

        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
            EUDReturn()
        EUDEndIf()

        if EUDIf()(v_mode == MODE_CONFIG):
            if EUDIf()(appManager.keyPress("Y", hold = ["LCTRL"])):
                v_mode << MODE_EXPORTING
                writeStrings()
            EUDEndIf()
        if EUDElse()():
            new_written = appManager.exportAppOutputToBridge(storage + written, remaining_bytes)

            remaining_bytes -= new_written
            written += new_written
            if EUDIf()(remaining_bytes == 0):
                v_mode << MODE_CONFIG
            EUDEndIf()
        EUDEndIf()
        appManager.requestUpdate()

    def print(self, writer):
        writer.write_f("String Editor - Exporter (Bridge Client required)\n")
        if EUDIf()(v_mode == MODE_CONFIG):
            writer.write_f("\n\x16Press CTRL+Y to EXPORT\n")
        if EUDElse()():
            writer.write_f("\x13Sent %D bytes / Remaining %D bytes\n\n\n\n", written, remaining_bytes)
        EUDEndIf()

        writer.write(0)
