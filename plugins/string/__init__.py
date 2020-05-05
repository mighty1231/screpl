from eudplib import *

from repl import REPL, getAppManager, AppCommand, EUDByteRW, f_raiseWarning

# initialize variables
appManager = getAppManager()
superuser = appManager.superuser
STRSection, STRSection_epd = f_dwepdread_epd(EPD(0x5993D4))

STRING_BUFFER_SZ = 200000
string_buffer = Db(STRING_BUFFER_SZ)
string_buffer_end = string_buffer + STRING_BUFFER_SZ
new_alloc_epd = EUDVariable(EPD(string_buffer))

string_count = f_dwread_epd(STRSection_epd)

cur_string_id = EUDVariable(1)
cur_string_offset_epd = EUDVariable()
cur_string_offset_epd << STRSection_epd + 1

from eudplib.eudlib.stringf.cputf8 import cp949_table
cvtb = [0] * 65536
for (ch1, ch2), tab in cp949_table:
    cvtb[ch1 + ch2 * 256] = tab
cvtb = EUDArray(cvtb)

@EUDFunc
def allocateForBuffer(string_id):
    global new_alloc_epd
    '''
    input: string id
    output: UTF-8 + Easy-to-modify-transformed new string epd pointer
            if fails, return 0 (already allocated / no more space)

    It modifies string offset pointer.
    '''
    # write 0x0D containing bytes
    string_offset_epd = STRSection_epd + string_id
    string_ptr = STRSection + f_dwread_epd(string_offset_epd)
    if EUDIf()([string_ptr >= string_buffer, string_ptr <= (string_buffer_end - 1)]):
        EUDReturn(EPD(string_ptr)) # already allocated
    EUDEndIf()

    cur_epd = EUDVariable()
    reader = EUDByteRW()
    reader.seekoffset(string_ptr)

    # for each character, allocate 4byte containing prefix 0xD
    cur_epd << new_alloc_epd
    is_utf8 = UTF8Check(string_ptr)
    if EUDIf()(is_utf8 == 1):
        if EUDInfLoop()():
            # buffer check
            if EUDIf()(cur_epd >= EPD(string_buffer_end)):
                f_raiseWarning("Warning: No more space for string buffer")
                EUDReturn(0)
            EUDEndIf()

            b1 = reader.read()
            EUDBreakIf(b1 == 0)
            if EUDIf()(b1 < 128):
                f_dwwrite_epd(cur_epd, 0x0D0D0D + b1*0x01000000)
            if EUDElseIf()(b1.ExactlyX(0b11000000, 0b11100000)):
                b2 = reader.read()
                f_dwwrite_epd(cur_epd, 0x0D0D + b1*0x10000 + b2*0x1000000)
            if EUDElseIf()(b1.ExactlyX(0b11100000, 0b11110000)):
                b2 = reader.read()
                b3 = reader.read()
                f_dwwrite_epd(cur_epd, 0x0D + b1*0x100 + b2*0x10000 +b3*0x1000000)
            EUDEndIf()
            cur_epd += 1
        EUDEndInfLoop()
    if EUDElse()():
        # cp949 to utf8
        if EUDInfLoop()():
            # buffer check
            if EUDIf()(cur_epd >= EPD(string_buffer_end)):
                f_raiseWarning("Warning: No more space for string buffer")
                EUDReturn(0)
            EUDEndIf()

            b1 = reader.read()
            EUDBreakIf(b1 == 0)
            if EUDIf()(b1 < 128):
                f_dwwrite_epd(cur_epd, 0x0D0D0D + b1*0x01000000)
            if EUDElse()():
                b2 = reader.read()
                EUDBreakIf(b2 == 0)
                ucode = cvtb[b2 * 256 + b1]
                if EUDIf()(ucode <= 0x07FF):
                    '''
                    ucode  : 0bxxxxxyyyyyy
                    result : 0x0D 0x0D 0b110xxxxx 0b10yyyyyy
                    '''
                    value = EUDVariable()
                    value << (0b10000000110000000000000000000000 + 0x0D0D)
                    for i in range(5+6):
                        j = i + 24 if i < 6 else i + 10
                        Trigger(
                            conditions = ucode.ExactlyX(1 << i, 1 << i),
                            actions = value.SetNumberX(1 << j, 1 << j)
                        )
                    f_dwwrite_epd(cur_epd, value)
                if EUDElse()():
                    '''
                    ucode  : 0bxxxxyyyyyyzzzzzz
                    result : 0x0D 0x1110xxxx 0b10yyyyyy 0b10zzzzzz
                    '''
                    value = EUDVariable()
                    value << (0b10000000100000001110000000000000 + 0x0D)
                    for i in range(4+6+6):
                        j = i + 24 if i < 6 else (i + 10 if i < 12 else i - 4)
                        Trigger(
                            conditions = ucode.ExactlyX(1 << i, 1 << i),
                            actions = value.SetNumberX(1 << j, 1 << j)
                        )
                    f_dwwrite_epd(cur_epd, value)
                EUDEndIf()
            EUDEndIf()
            cur_epd += 1
        EUDEndInfLoop()
    EUDEndIf()
    f_dwwrite_epd(cur_epd, 0)

    # Extra space. Give more spaces.
    ret_epd = EUDVariable()
    epd_diff = cur_epd - new_alloc_epd
    ret_epd << new_alloc_epd
    new_alloc_epd += (epd_diff + 500)

    f_dwwrite_epd(string_offset_epd, (ret_epd - STRSection_epd) * 4)

    EUDReturn(ret_epd)

@EUDFunc
def UTF8Check(offset):
    '''
    if string starts with OFFSET is utf-8 decodable, return 1
    otherwise 0
    '''
    reader = EUDByteRW()
    reader.seekoffset(offset)

    if EUDInfLoop()():
        b = reader.read()
        EUDBreakIf(b == 0)

        if EUDIf()(b.ExactlyX(0b00000000, 0b10000000)):
            # unicode 0 - 0x7F (ascii)
            pass
        if EUDElseIf()(b.ExactlyX(0b11000000, 0b11100000)):
            # unicode 0x80 - 0x7FF
            b2 = reader.read()
            if EUDIfNot()(b2.ExactlyX(0b10000000, 0b11000000)):
                EUDReturn(0)
            EUDEndIf()
        if EUDElseIf()(b.ExactlyX(0b11100000, 0b11110000)):
            # unicode 0x800 - 0xFFFF
            if EUDLoopN()(2):
                b3 = reader.read()
                if EUDIfNot()(b3.ExactlyX(0b10000000, 0b11000000)):
                    EUDReturn(0)
                EUDEndIf()
            EUDEndLoopN()
        if EUDElse()():
            # do not consider the case for unicode > 0x10000
            EUDReturn(0)
        EUDEndIf()
    EUDEndInfLoop()

    EUDReturn(1)

@EUDFunc
def f_strcpy_epd(dstepdp, srcepdp):
    '''
    dstepdp <- srcepdp
    returns updated dstepdp
    '''
    cpmoda = Forward()

    VProc([dstepdp, srcepdp], [
        SetMemory(cpmoda, SetTo, -1),
        dstepdp.QueueAddTo(EPD(cpmoda)),
        srcepdp.SetDest(EPD(0x6509B0))
    ])

    if EUDInfLoop()():
        cpmod = f_dwread_cp(0)
        cpmoda << cpmod.getDestAddr()

        VProc(cpmod, [
            cpmod.AddDest(1),
            SetMemory(0x6509B0, Add, 1)
        ])

        EUDBreakIf(cpmod.Exactly(0))
    EUDEndInfLoop()

    f_setcurpl2cpcache()

    # EUDReturn(f_dwread_epd(EPD(cpmoda)))

# make commands
from .manager import StringManagerApp

@AppCommand([])
def startCommand(self):
    appManager.startApplication(StringManagerApp)

REPL.addCommand('string', startCommand)
