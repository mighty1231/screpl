
from eudplib import *

from screpl.core.application import Application
from screpl.utils.debug import f_raise_warning

from . import *

v_string_epd = EUDVariable()
v_cursor_epd = EUDVariable()
v_frame = EUDVariable(0)

# if string is not changed, restore previous string pointer
v_changed = EUDVariable()
v_oldbuf_offset = EUDVariable()
v_previous_alloc_epd = EUDVariable()

BLINK_PERIOD = 4

MODE_INSERT = 0
MODE_OVERWRITE = 1
v_mode = EUDVariable(MODE_INSERT)

tmp_storage = Db(10000)
tmp_storage_epd = EPD(tmp_storage)

DISPMODE_MAIN = 0
DISPMODE_MANUAL = 1
v_dispmode = EUDVariable()

class StringEditorApp(Application):
    def on_init(self):
        v_mode << MODE_INSERT
        string_offset_epd = STRSection_epd + cur_string_id
        v_oldbuf_offset << f_dwread_epd(string_offset_epd)
        string_ptr = STRSection + v_oldbuf_offset
        if EUDIf()([string_ptr >= string_buffer, string_ptr <= (string_buffer_end - 1)]):
            # already allocated
            v_changed << 1
            v_string_epd << EPD(string_ptr)
        if EUDElse()():
            v_changed << 0
            v_previous_alloc_epd << new_alloc_epd
            v_string_epd << allocate_for_buffer(cur_string_id)
        EUDEndIf()
        v_cursor_epd << v_string_epd
        v_dispmode << DISPMODE_MAIN

    def on_destruct(self):
        if EUDIf()(v_changed == 0):
            # fill null bytes for allocated buffer
            temp_epd = EUDVariable()
            temp_epd << v_previous_alloc_epd
            cond, act = Forward(), Forward()

            # cur_epd = v_previous_alloc_epd
            SeqCompute([
                (EPD(cond + 4), SetTo, EPD(act + 16)),
                (EPD(cond + 8), SetTo, new_alloc_epd),
                (EPD(act + 16), SetTo, v_previous_alloc_epd),
            ])
            if EUDInfLoop()():
                EUDBreakIf(cond << Memory(0, AtLeast, 0)) # Memory(cur_epd, AtLeast, new_alloc_epd)

                DoActions([
                    act << SetMemory(0, SetTo, 0), # SetMemory(cur_epd, Add, 1)
                    SetMemory(act + 16, Add, 1),   # cur_epd += 1
                ])
            EUDEndInfLoop()

            # restore pointers
            f_dwwrite_epd(STRSection_epd + cur_string_id, v_oldbuf_offset)
            new_alloc_epd << v_previous_alloc_epd
        EUDEndIf()

    def on_chat(self, address):
        global v_cursor_epd

        v_changed << 1

        reader = REPLByteRW()
        reader.seekoffset(address)
        clear_overwrite, clear_insert = Forward(), Forward()
        continue_overwrite, continue_insert = Forward(), Forward()
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
                    if EUDElseIf()(eb2 == ord('n')):
                        b1 << ord('\n')
                    if EUDElseIf()(eb2 == ord('t')):
                        b1 << ord('\t')
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
                                f_raise_warning("Wrong usage on string escape. Press F1.")
                                EUDJump(clear_overwrite)
                            EUDEndIf()
                            if nnn == 0:
                                b1 *= 16
                        if EUDIf()(b1 >= 0x80):
                            f_raise_warning("Writing \\x80~\\xFF is prohibited. Instead, use \\u####")
                            EUDJump(clear_overwrite)
                        EUDEndIf()
                    if EUDElseIf()(eb2 == ord('u')):
                        b1 << 0
                        for nnn in range(4):
                            hexb = reader.read()
                            if EUDIf()([hexb >= ord('0'), hexb <= ord('9')]):
                                b1 += (hexb - ord('0'))
                            if EUDElseIf()([hexb >= ord('a'), hexb <= ord('f')]):
                                b1 += (hexb - ord('a') + 10)
                            if EUDElseIf()([hexb >= ord('A'), hexb <= ord('F')]):
                                b1 += (hexb - ord('A') + 10)
                            if EUDElse()():
                                f_raise_warning("Wrong usage on string escape. Press F1.")
                                EUDJump(clear_overwrite)
                            EUDEndIf()
                            if nnn != 3:
                                b1 *= 16
                        if EUDIfNot()(b1 <= 0x7F):
                            if EUDIf()(b1 <= 0x7FF):
                                '''
                                b1  : 0bxxxxxyyyyyy
                                result : 0x0D 0x0D 0b110xxxxx 0b10yyyyyy
                                '''
                                value = EUDVariable()
                                value << (0b10000000110000000000000000000000 + 0x0D0D)
                                for i in range(5+6):
                                    j = i + 24 if i < 6 else i + 10
                                    Trigger(
                                        conditions=b1.ExactlyX(1 << i, 1 << i),
                                        actions=value.SetNumberX(1 << j, 1 << j)
                                    )
                                f_dwwrite_epd(v_cursor_epd, value)
                            if EUDElse()():
                                '''
                                b1  : 0bxxxxyyyyyyzzzzzz
                                result : 0x0D 0x1110xxxx 0b10yyyyyy 0b10zzzzzz
                                '''
                                value = EUDVariable()
                                value << (0b10000000100000001110000000000000 + 0x0D)
                                for i in range(4+6+6):
                                    j = i + 24 if i < 6 else (i + 10 if i < 12 else i - 4)
                                    Trigger(
                                        conditions=b1.ExactlyX(1 << i, 1 << i),
                                        actions=value.SetNumberX(1 << j, 1 << j)
                                    )
                                f_dwwrite_epd(v_cursor_epd, value)
                            EUDEndIf()
                            EUDJump(continue_overwrite)
                        EUDEndIf()
                    if EUDElse()():
                        f_raise_warning("Wrong usage on string escape. Press F1.")
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

                continue_overwrite << NextTrigger()
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
                    if EUDElseIf()(eb2 == ord('n')):
                        b1 << ord('\n')
                    if EUDElseIf()(eb2 == ord('t')):
                        b1 << ord('\t')
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
                                f_raise_warning("Wrong usage on string escape. Press F1.")
                                EUDJump(clear_insert)
                            EUDEndIf()
                            if nnn == 0:
                                b1 *= 16
                        if EUDIf()(b1 >= 0x80):
                            f_raise_warning("Writing \\x80~\\xFF is prohibited. Instead, use \\u####")
                            EUDJump(clear_insert)
                        EUDEndIf()
                    if EUDElseIf()(eb2 == ord('u')):
                        b1 << 0
                        for nnn in range(4):
                            hexb = reader.read()
                            if EUDIf()([hexb >= ord('0'), hexb <= ord('9')]):
                                b1 += (hexb - ord('0'))
                            if EUDElseIf()([hexb >= ord('a'), hexb <= ord('f')]):
                                b1 += (hexb - ord('a') + 10)
                            if EUDElseIf()([hexb >= ord('A'), hexb <= ord('F')]):
                                b1 += (hexb - ord('A') + 10)
                            if EUDElse()():
                                f_raise_warning("Wrong usage on string escape. Press F1.")
                                EUDJump(clear_insert)
                            EUDEndIf()
                            if nnn != 3:
                                b1 *= 16
                        if EUDIfNot()(b1 <= 0x7F):
                            if EUDIf()(b1 <= 0x7FF):
                                '''
                                b1  : 0bxxxxxyyyyyy
                                result : 0x0D 0x0D 0b110xxxxx 0b10yyyyyy
                                '''
                                value = EUDVariable()
                                value << (0b10000000110000000000000000000000 + 0x0D0D)
                                for i in range(5+6):
                                    j = i + 24 if i < 6 else i + 10
                                    Trigger(
                                        conditions=b1.ExactlyX(1 << i, 1 << i),
                                        actions=value.SetNumberX(1 << j, 1 << j)
                                    )
                                f_dwwrite_epd(v_cursor_epd, value)
                            if EUDElse()():
                                '''
                                b1  : 0bxxxxyyyyyyzzzzzz
                                result : 0x0D 0x1110xxxx 0b10yyyyyy 0b10zzzzzz
                                '''
                                value = EUDVariable()
                                value << (0b10000000100000001110000000000000 + 0x0D)
                                for i in range(4+6+6):
                                    j = i + 24 if i < 6 else (i + 10 if i < 12 else i - 4)
                                    Trigger(
                                        conditions=b1.ExactlyX(1 << i, 1 << i),
                                        actions=value.SetNumberX(1 << j, 1 << j)
                                    )
                                f_dwwrite_epd(v_cursor_epd, value)
                            EUDEndIf()
                            EUDJump(continue_insert)
                        EUDEndIf()
                    if EUDElse()():
                        f_raise_warning("Wrong usage on string escape. Press F1.")
                        EUDJump(clear_insert)
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

                continue_insert << NextTrigger()
                v_cursor_epd += 1
            EUDEndInfLoop()

            clear_insert << NextTrigger()
            f_strcpy_epd(v_cursor_epd, tmp_storage_epd)
        EUDEndIf()

    def loop(self):
        global v_cursor_epd, v_frame

        if EUDIf()(app_manager.key_press("ESC")):
            app_manager.request_destruct()
        if EUDElseIf()(app_manager.key_press("INSERT")):
            v_mode << 1 - v_mode
        if EUDElseIf()(app_manager.key_press("DELETE")):
            f_strcpy_epd(v_cursor_epd, v_cursor_epd + 1)
        if EUDElseIf()(app_manager.key_press("BACK")):
            if EUDIfNot()(v_cursor_epd == v_string_epd):
                v_cursor_epd -= 1
                f_strcpy_epd(v_cursor_epd, v_cursor_epd + 1)
            EUDEndIf()
        if EUDElseIf()(app_manager.key_press("F7")):
            if EUDIfNot()(v_cursor_epd == v_string_epd):
                v_cursor_epd -= 1
                v_frame << BLINK_PERIOD * 2 - 1
            EUDEndIf()
        if EUDElseIf()(app_manager.key_press("F8")):
            if EUDIfNot()(MemoryEPD(v_cursor_epd, Exactly, 0)):
                v_cursor_epd += 1
                v_frame << BLINK_PERIOD * 2 - 1
            EUDEndIf()
        if EUDElseIf()(app_manager.key_press("HOME")):
            if EUDInfLoop()():
                EUDBreakIf(v_cursor_epd == v_string_epd)
                v_cursor_epd -= 1
                if EUDIf()(MemoryEPD(v_cursor_epd, Exactly, 0x0D0D0D + ord('\n') * 0x01000000)):
                    v_cursor_epd += 1
                    EUDBreak()
                EUDEndIf()
            EUDEndInfLoop()
            v_frame << BLINK_PERIOD * 2 - 1
        if EUDElseIf()(app_manager.key_press("END")):
            if EUDInfLoop()():
                EUDBreakIf(MemoryEPD(v_cursor_epd, Exactly, 0))
                EUDBreakIf(MemoryEPD(v_cursor_epd, Exactly, 0x0D0D0D + ord('\n') * 0x01000000))
                v_cursor_epd += 1
            EUDEndInfLoop()
            v_frame << BLINK_PERIOD * 2 - 1
        if EUDElseIf()(app_manager.key_down("F1")):
            v_dispmode << DISPMODE_MANUAL
        if EUDElseIf()(app_manager.key_up("F1")):
            v_dispmode << DISPMODE_MAIN
        EUDEndIf()
        app_manager.request_update()

        v_frame += 1
        Trigger(
            conditions=v_frame.Exactly(BLINK_PERIOD * 2),
            actions=v_frame.SetNumber(0)
        )

    def print(self, writer):
        '''
        color_code : 0x01 - 0x1F
        except for 0x09 - 0x0D, 0x12, 0x13
        '''
        if EUDIf()(v_dispmode == DISPMODE_MAIN):
            global v_cursor_epd

            v_cursor_val, v_cursor_val2 = EUDCreateVariables(2)
            v_cursor_val  << f_dwread_epd(v_cursor_epd)
            v_cursor_val2 << f_dwread_epd(v_cursor_epd + 1)
            if EUDIf()(v_frame < BLINK_PERIOD):
                '''
                the way to show cursor
                cursor_epd     : 0D xx xx xx (0D -> '|' or color code)
                cursor_epd + 1 : 0D xx xx xx (0D -> restored color code )
                '''
                if EUDIf()(v_mode == MODE_OVERWRITE):
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

                if EUDElse()(): # insert
                    f_bwrite_epd(v_cursor_epd, 0, ord('|'))
                EUDEndIf()
            EUDEndIf()
            writer.write_strepd(v_string_epd)

            # restore string near cursor
            f_dwwrite_epd(v_cursor_epd, v_cursor_val)
            f_dwwrite_epd(v_cursor_epd + 1, v_cursor_val2)
        if EUDElse()():
            writer.write_f(
                "String Editor\n"
                "Chat any string to insert/overwrite on the cursor. "
                "Press BACKSPACE/DELETE to remove a character on the cursor.\n"
                "Press F7, F8, HOME, or END to move the cursor. "
                "Press INSERT to toggle insert/overwrite mode.\n"
                "Chat \\n (newline) \\t (tab) \\x## (bytecode) \\u#### (unicode) to insert special characters\n"
                "\\x12 Right Align \\x13 Center Align \\x0B \\x14 Invisible \\x0C Remove Beyond\n"
                "\x01\\x01 \x02\\x02 \x03\\x03 \x04\\x04 \x06\\x06 \x07\\x07 \x08\\x08 \x0E\\x0E \x0F\\x0F \x10\\x10 \x11\\x11\n"
                "\x15\\x15 \x16\\x16 \x17\\x17 \x18\\x18 \x19\\x19 \x1A\\x1A \x1B\\x1B \x1C\\x1C \x1D\\x1D \x1E\\x1E \x1F\\x1F\n"
                "\x02\\uac00 \uac00 \\u2606 \u2606 \x05\\x05 Grey\n"
            )
        EUDEndIf()
        writer.write(0)
