"""StringSearchApp

TUI - <no result> case

.. code-block:: text

    1. Results {""} not found, search string with chat.

<result> case

.. code-block:: text

    1. Search results "{string}", %D / Total %D found.
    2.  ##. {found line}
    3.  ##. {found line}

Feature
 * Search with plain text, prints rich text

pseudocode
global variable

* count: searched count
* searched_ids: array of string id that contains target
* searched_string: array of lines containing target

input

  * target : given string

code:

.. code-block:: c

    for each string_id:
        char *ptr = get_string_ptr(string_id)
        while (*ptr != 0){
            // make utf-8, remove color code
            length, is_null_end = _strcpy_until_newline(line_buffer, ptr)

            // use KMP search
            // https://www.geeksforgeeks.org/kmp-algorithm-for-pattern-searching/
            found = KMPSearch(line_buffer, target)
            if (found) {
                searched_ids[count] = string_id;
                searched_strings[count] = allocate_line(ptr);
                count ++;
                break;
            }
            if (is_null_end)
                break;
            if (is_null_end):
                break
            else
                ptr += length + 1
        }
"""
from eudplib import *

from screpl.core.application import Application
from screpl.utils.byterw import REPLByteRW
from screpl.utils.string import f_strlen

from . import *

MAX_SEARCH_CNT = 4096
LINE_BUF_SZ = 300

# query statement, utf-8
db_target = Db(220)

# used on KMP
db_lps = EUDArray(LINE_BUF_SZ)

# buffer for search results, utf-8
db_result_buffer = Db(100000)
v_next_empty_result_buffer = EUDVariable(db_result_buffer)
db_line_buffer = Db(LINE_BUF_SZ)

# search results
v_focused = EUDVariable(0) # searching_index
v_search_cnt = EUDVariable(0)
v_search_ids = EUDArray(MAX_SEARCH_CNT)
v_search_strings = EUDArray(MAX_SEARCH_CNT)

v_return_epd = EUDVariable(0)

v_is_utf8 = EUDVariable()

def _strcpy_until_newline(v_ptr):
    reader, writer = REPLByteRW(), REPLByteRW()
    reader.seekoffset(v_ptr)
    writer.seekepd(EPD(db_line_buffer))
    is_null_end = EUDVariable()
    is_null_end << 1
    if EUDIf()(v_is_utf8):
        if EUDInfLoop()():
            b1 = reader.read()
            EUDBreakIf(b1 == 0)

            if EUDIf()(b1 < 128):
                # copy only \t between 0x00~0x1F
                if EUDIf()([b1 == ord('\t')]):
                    writer.write(b1)
                if EUDElseIf()(b1 == ord('\n')):
                    is_null_end << 0
                    EUDBreak()
                if EUDElseIf()(b1 >= 0x20):
                    writer.write(b1)
                EUDEndIf()
            if EUDElseIf()(b1.ExactlyX(0b11000000, 0b11100000)):
                b2 = reader.read()
                writer.write(b1)
                writer.write(b2)
            if EUDElseIf()(b1.ExactlyX(0b11100000, 0b11110000)):
                b2 = reader.read()
                b3 = reader.read()
                writer.write(b1)
                writer.write(b2)
                writer.write(b3)
            EUDEndIf()
        EUDEndInfLoop()
    if EUDElse()(): # cp949
        if EUDInfLoop()():
            b1 = reader.read()
            EUDBreakIf(b1 == 0)

            if EUDIf()(b1 < 128):
                # copy only \t between 0x00~0x1F
                if EUDIf()([b1 == ord('\t')]):
                    writer.write(b1)
                if EUDElseIf()(b1 == ord('\n')):
                    is_null_end << 0
                    EUDBreak()
                if EUDElseIf()(b1 >= 0x20):
                    writer.write(b1)
                EUDEndIf()
            if EUDElse()():
                b2 = reader.read()
                EUDBreakIf(b2 == 0)
                ucode = cvtb[b2 * 256 + b1]
                if EUDIf()(ucode <= 0x07FF):
                    '''
                    ucode  : 0bxxxxxyyyyyy
                    result : 0b110xxxxx 0b10yyyyyy
                    '''
                    ch1, ch2 = EUDCreateVariables(2)
                    ch1 << 0b11000000
                    ch2 << 0b10000000
                    for i in range(5+6):
                        if i < 6:
                            ch = ch2
                            j = i
                        else:
                            ch = ch1
                            j = i - 6
                        Trigger(
                            conditions=ucode.ExactlyX(1 << i, 1 << i),
                            actions=ch.SetNumberX(1 << j, 1 << j)
                        )
                    writer.write(ch1)
                    writer.write(ch2)
                if EUDElse()():
                    '''
                    ucode  : 0bxxxxyyyyyyzzzzzz
                    result : 0x1110xxxx 0b10yyyyyy 0b10zzzzzz
                    '''
                    ch1, ch2, ch3 = EUDCreateVariables(3)
                    ch1 << 0b11100000
                    ch2 << 0b10000000
                    ch3 << 0b10000000
                    for i in range(4+6+6):
                        if i < 6:
                            ch = ch3
                            j = i
                        elif i < 12:
                            ch = ch2
                            j = i - 6
                        else:
                            ch = ch1
                            j = i - 12
                        Trigger(
                            conditions=ucode.ExactlyX(1 << i, 1 << i),
                            actions=ch.SetNumberX(1 << j, 1 << j)
                        )
                    writer.write(ch1)
                    writer.write(ch2)
                    writer.write(ch3)
                EUDEndIf()
            EUDEndIf()
        EUDEndInfLoop()
    EUDEndIf()
    writer.write(0)
    return reader.getoffset() - v_ptr - 1, is_null_end

def _compute_lps_array(pattern):
    '''
    KMP Search preprocessing - evaluate LPS array
    '''
    i, length = EUDCreateVariables(2)
    preader = REPLByteRW()
    cond = Forward()

    DoActions([length.SetNumber(0), i.SetNumber(1)])
    SeqCompute([(EPD(cond + 8), SetTo, 0)])
    preader.seekoffset(pattern + 1)
    if EUDInfLoop()():
        if EUDIfNot()(cond << Memory(i.getValueAddr(), Exactly, 0)):
            b = preader.read()
            SeqCompute([(EPD(cond + 8), SetTo, i)])
            EUDBreakIf(b.Exactly(0))
        EUDEndIf()

        if EUDIf()(b == f_bread(pattern + length)):
            length += 1
            DoActions([
                SetMemoryEPD(EPD(db_lps) + i, SetTo, length),
                i.AddNumber(1)
            ])
        if EUDElse()():
            if EUDIfNot()(length.Exactly(0)):
                length << db_lps[length - 1]
            if EUDElse()():
                DoActions([
                    SetMemoryEPD(EPD(db_lps) + i, SetTo, 0),
                    i.AddNumber(1)
                ])
            EUDEndIf()
        EUDEndIf()
    EUDEndInfLoop()

@EUDFunc
def KMPSearch(pattern):
    '''
    Search string starts with PTR on db_line_buffer
    '''
    treader, preader = REPLByteRW(), REPLByteRW()
    i, j = EUDCreateVariables(2)

    treader.seekepd(EPD(db_line_buffer))
    preader.seekoffset(pattern)
    i << 0 # index for txt
    j << 0 # index for pattern
    tb = treader.read()
    pb = preader.read()
    if EUDInfLoop()():
        EUDBreakIf(tb.Exactly(0))
        if EUDIf()(tb == pb):
            DoActions([i.AddNumber(1), j.AddNumber(1)])
            tb << treader.read()
            pb << preader.read()
        EUDEndIf()

        if EUDIf()(pb == 0):
            # found pattern
            EUDReturn(1)
        if EUDElseIfNot()([tb.Exactly(0)]):
            # mismatch after j matches 
            if EUDIfNot()(pb == tb):
                # Do not match lps[0..lps[j-1]] characters,
                # they will match anyway
                if EUDIfNot()(j == 0):
                    j << db_lps[j-1]
                    preader.seekoffset(pattern + j)
                    pb << preader.read()
                if EUDElse()():
                    DoActions(i.AddNumber(1))
                    tb << treader.read()
                EUDEndIf()
            EUDEndIf()
        EUDEndIf()
    EUDEndInfLoop()
    EUDReturn(0)

@EUDFunc
def _focus_result(new_focus):
    if EUDIfNot()(new_focus >= v_search_cnt):
        if EUDIfNot()(new_focus == v_focused):
            v_focused << new_focus
            app_manager.request_update()
        EUDEndIf()
    EUDEndIf()

class StringSearchApp(Application):
    @staticmethod
    def set_return_epd(return_epd):
        v_return_epd << return_epd

    def on_destruct(self):
        if EUDIf()([v_return_epd >= 1, v_search_cnt >= 1]):
            f_dwwrite_epd(v_return_epd, v_search_ids[v_focused])
        EUDEndIf()
        v_return_epd << 0

    def on_chat(self, address):
        v_string_id, v_result_line_ptr = EUDCreateVariables(2)
        c_dupcheck = Forward()
        trig_cpoint = Forward() # continue point
        result_buf_writer = REPLByteRW()

        # evaluate LPS array
        # https://www.geeksforgeeks.org/kmp-algorithm-for-pattern-searching/
        _compute_lps_array(address)

        v_search_cnt << 0
        v_string_id << 1
        v_result_line_ptr << db_result_buffer
        result_buf_writer.seekepd(EPD(db_result_buffer))
        if EUDInfLoop()():
            offset = f_dwread_epd(STRSection_epd + v_string_id)

            # prevent double search over same offset
            EUDJumpIf(c_dupcheck << offset.Exactly(0), trig_cpoint)
            SeqCompute([(EPD(c_dupcheck + 8), SetTo, offset)])

            v_textptr = STRSection + offset
            v_is_utf8 << f_check_utf8(v_textptr)
            if EUDInfLoop()():
                ch = f_bread(v_textptr)
                EUDBreakIf(ch == 0)

                length, is_null_end = _strcpy_until_newline(v_textptr)
                found = KMPSearch(address)
                if EUDIf()(found == 1):
                    DoActions([
                        SetMemoryEPD(EPD(v_search_ids) + v_search_cnt, SetTo, v_string_id),
                        SetMemoryEPD(EPD(v_search_strings) + v_search_cnt, SetTo, v_result_line_ptr),
                        v_search_cnt.AddNumber(1)
                    ])

                    # allocate line
                    result_buf_writer.write_f("%E", EPD(db_line_buffer))
                    result_buf_writer.write(0)
                    v_result_line_ptr << result_buf_writer.getoffset()

                    EUDBreak()
                EUDEndIf()

                EUDBreakIf(is_null_end == 1)
                v_textptr += length + 1
            EUDEndInfLoop()

            # continue point
            trig_cpoint << NextTrigger()
            EUDBreakIf(v_string_id >= string_count)
            v_string_id += 1
        EUDEndInfLoop()

        writer = REPLByteRW()
        writer.seekepd(EPD(db_target))
        writer.write_str(address)
        writer.write(0)
        v_focused << 0

    def loop(self):
        if EUDIf()(app_manager.key_press("ESC")):
            app_manager.request_destruct()
            EUDReturn()
        if EUDElseIf()(app_manager.key_press('F7')):
            _focus_result(v_focused-1)
        if EUDElseIf()(app_manager.key_press('F8')):
            _focus_result(v_focused+1)
        EUDEndIf()
        app_manager.request_update()

    def print(self, writer):
        if EUDIf()(v_search_cnt == 0):
            writer.write_f("Search results \"%E\" - not found\n" + "\n" * 8,
                           EPD(db_target))
        if EUDElse()():
            writer.write_f("Search results \"%E\" - %D / total %D found\n",
                           EPD(db_target),
                           v_focused,
                           v_search_cnt)

            quot, mod = f_div(v_focused, 8)
            cur = quot * 8
            pageend = cur + 8
            until = EUDVariable()
            if EUDIf()(pageend <= v_search_cnt):
                until << pageend
            if EUDElse()():
                until << v_search_cnt
            EUDEndIf()

            # fill contents
            if EUDInfLoop()():
                EUDBreakIf(cur >= until)

                if EUDIf()(cur == v_focused):
                    writer.write(0x11) # orange
                if EUDElse()():
                    writer.write(0x02) # pale blue
                EUDEndIf()

                writer.write_f(" %D: %S\n",
                               v_search_ids[cur],
                               v_search_strings[cur])

                DoActions([cur.AddNumber(1)])
            EUDEndInfLoop()
        EUDEndIf()
        writer.write(0)
