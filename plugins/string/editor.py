from eudplib import *
from repl import (
    Application,
    AppTypedMethod,
    AppCommand,
    argEncNumber,
    Logger,
    f_raiseWarning
)

from . import *

v_string_epd = EUDVariable()
v_cursor_epd = EUDVariable()
v_frame = EUDVariable(0)

BLINK_PERIOD = 4

MODE_INSERT = 0
MODE_OVERWRITE = 1
v_mode = EUDVariable(MODE_INSERT)

tmp_storage = Db(10000)
tmp_storage_epd = EPD(tmp_storage)

class StringEditorApp(Application):
    def onInit(self):
        v_string_epd << allocateForBuffer(cur_string_id)
        v_cursor_epd << v_string_epd

    def onChat(self, offset):
        global v_cursor_epd

        reader = EUDByteRW()
        reader.seekoffset(offset)
        clear_overwrite, clear_insert = Forward(), Forward()
        if EUDIf()(v_mode == MODE_OVERWRITE):
            null_met = EUDVariable()
            null_met << 0
            if EUDInfLoop()():
                b1 = reader.read()
                EUDBreakIf(b1 == 0)

                # string became longer
                if EUDIf()(MemoryEPD(v_cursor_epd, Exactly, 0)):
                    null_met << 1
                EUDEndIf()

                # string escape character
                if EUDIf()(b1 == ord('\\')):
                    eb2 = reader.read()
                    if EUDIf()(eb2 == ord('\\')):
                        b1 << ord('\\')
                    if EUDElseIf()(eb2 == ord('x')):
                        b1 << 0
                        for nnn in range(2):
                            hexb = reader.read()
                            if EUDIf()([hexb >= ord('0'), hexb <= ord('9')]):
                                b1 += (hexb - ord('0'))
                            if EUDElseIf()([hexb >= ord('a'), hexb <= ord('f')]):
                                b1 += (hexb - ord('a') + 10)
                            if EUDElseIf()([hexb >= ord('A'), hexb <= ord('F')]):
                                b1 += (hexb - ord('A') + 10)
                            if EUDElse()():
                                f_raiseWarning("String escape character '\\' usage-> '\\\\' or '\\x##'")
                                EUDJump(clear_overwrite)
                            EUDEndIf()
                            if nnn == 0:
                                b1 *= 16
                    if EUDElse()():
                        f_raiseWarning("String escape character '\\' usage-> '\\\\' or '\\x##'")
                        EUDJump(clear_overwrite)
                    EUDEndIf()
                EUDEndIf()

                if EUDIf()(b1 < 128):
                    f_dwwrite_epd(v_cursor_epd, 0x0D0D0D + b1*0x01000000)
                if EUDElseIf()(b1.ExactlyX(0b11000000, 0b11100000)):
                    b2 = reader.read()
                    f_dwwrite_epd(v_cursor_epd, 0x0D0D + b1*0x10000 + b2*0x1000000)
                if EUDElseIf()(b1.ExactlyX(0b11100000, 0b11110000)):
                    b2 = reader.read()
                    b3 = reader.read()
                    f_dwwrite_epd(v_cursor_epd, 0x0D + b1*0x100 + b2*0x10000 + b3*0x1000000)
                EUDEndIf()
                v_cursor_epd += 1
            EUDEndInfLoop()

            clear_overwrite << NextTrigger()
            if EUDIf()(null_met == 1):
                f_dwwrite_epd(v_cursor_epd, 0)
            EUDEndIf()
        if EUDElse()(): # insert mode
            f_strcpy_epd(tmp_storage_epd, v_cursor_epd)
            if EUDInfLoop()():
                b1 = reader.read()
                EUDBreakIf(b1 == 0)

                # string escape character
                if EUDIf()(b1 == ord('\\')):
                    eb2 = reader.read()
                    if EUDIf()(eb2 == ord('\\')):
                        b1 << ord('\\')
                    if EUDElseIf()(eb2 == ord('x')):
                        b1 << 0
                        for nnn in range(2):
                            hexb = reader.read()
                            if EUDIf()([hexb >= ord('0'), hexb <= ord('9')]):
                                b1 += (hexb - ord('0'))
                            if EUDElseIf()([hexb >= ord('a'), hexb <= ord('f')]):
                                b1 += (hexb - ord('a') + 10)
                            if EUDElseIf()([hexb >= ord('A'), hexb <= ord('F')]):
                                b1 += (hexb - ord('A') + 10)
                            if EUDElse()():
                                f_raiseWarning("String escape character '\\' usage-> '\\\\' or '\\x##'")
                                EUDJump(clear_overwrite)
                            EUDEndIf()
                            if nnn == 0:
                                b1 *= 16
                    if EUDElse()():
                        f_raiseWarning("String escape character '\\' usage-> '\\\\' or '\\x##'")
                        EUDJump(clear_overwrite)
                    EUDEndIf()
                EUDEndIf()

                if EUDIf()(b1 < 128):
                    f_dwwrite_epd(v_cursor_epd, 0x0D0D0D + b1*0x01000000)
                if EUDElseIf()(b1.ExactlyX(0b11000000, 0b11100000)):
                    b2 = reader.read()
                    f_dwwrite_epd(v_cursor_epd, 0x0D0D + b1*0x10000 + b2*0x1000000)
                if EUDElseIf()(b1.ExactlyX(0b11100000, 0b11110000)):
                    b2 = reader.read()
                    b3 = reader.read()
                    f_dwwrite_epd(v_cursor_epd, 0x0D + b1*0x100 + b2*0x10000 +b3*0x1000000)
                EUDEndIf()
                v_cursor_epd += 1
            EUDEndInfLoop()

            clear_insert << NextTrigger()
            f_strcpy_epd(v_cursor_epd, tmp_storage_epd)
        EUDEndIf()

    def loop(self):
        global v_cursor_epd, v_frame

        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
        if EUDElseIf()(appManager.keyPress("insert")):
            v_mode << 1 - v_mode
        if EUDElseIf()(appManager.keyPress("delete")):
            f_strcpy_epd(v_cursor_epd, v_cursor_epd + 1)
        if EUDElseIf()(appManager.keyPress("F7")):
            if EUDIfNot()(v_cursor_epd == v_string_epd):
                v_cursor_epd -= 1
            EUDEndIf()
        if EUDElseIf()(appManager.keyPress("F8")):
            if EUDIfNot()(f_dwread_epd(v_cursor_epd) == 0):
                v_cursor_epd += 1
            EUDEndIf()
        EUDEndIf()
        appManager.requestUpdate()

        v_frame += 1
        Trigger(
            conditions = v_frame.Exactly(BLINK_PERIOD * 2),
            actions = v_frame.SetNumber(0)
        )

    def print(self, writer):
        '''
        color_code : 0x01 - 0x1F
        except for 0x09 - 0x0D, 0x12, 0x13
        '''
        global v_cursor_epd

        v_cursor_val, v_cursor_val2 = EUDCreateVariables(2)
        v_cursor_val  << f_dwread_epd(v_cursor_epd)
        v_cursor_val2 << f_dwread_epd(v_cursor_epd + 1)
        if EUDIf()(v_frame >= BLINK_PERIOD):
            # emphasize
            if EUDIf()(v_mode == MODE_OVERWRITE):
                '''
                the way to emphasize the cursor
                cursor_epd     : 0D xx xx xx (0D -> '|' or color code)
                cursor_epd + 1 : 0D xx xx xx (0D -> restored color code )
                '''
                v_color, v_tmp_epd = EUDCreateVariables(2)

                v_color << 0x01 # default color code
                v_tmp_epd << v_string_epd
                if EUDInfLoop()():
                    EUDBreakIf(v_cursor_epd <= v_tmp_epd)
                    if EUDIf()(MemoryXEPD(v_tmp_epd, AtMost, 0x1F000000, 0xFF000000)):
                        code = f_bread_epd(v_tmp_epd, 3)
                        if EUDIfNot()([code >= 0x09, code <= 0x0D]):
                            if EUDIfNot()([code >= 0x12, code <= 0x13]):
                                v_color << code
                            EUDEndIf()
                        EUDEndIf()
                    EUDEndIf()
                    v_tmp_epd += 1
                EUDEndInfLoop()

                # write color code
                if EUDIf()(v_color == 0x11):
                    f_bwrite_epd(v_cursor_epd, 0, 0x0E)
                if EUDElse()():
                    f_bwrite_epd(v_cursor_epd, 0, 0x11)
                EUDEndIf()
                f_bwrite_epd(v_cursor_epd + 1, 0, v_color) # restoring color
                Logger.format("EPD %H colorcode %D", v_string_epd, v_color)

            if EUDElse()(): # insert
                f_bwrite_epd(v_cursor_epd, 0, ord('|'))
            EUDEndIf()
        EUDEndIf()
        writer.write_strepd(v_string_epd)
        writer.write(0)

        # restore string near cursor
        f_dwwrite_epd(v_cursor_epd, v_cursor_val)
        f_dwwrite_epd(v_cursor_epd + 1, v_cursor_val2)
