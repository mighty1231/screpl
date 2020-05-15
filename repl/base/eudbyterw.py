from eudplib import *
from ..utils import EPDConstString

class EUDByteRW:
    def __init__(self):
        self.epd, self.off = EUDCreateVariables(2)

    @EUDMethod
    def getoffset(self):
        EUDReturn(0x58A364 + 4 * self.epd + self.off)

    def seekepd(self, epd):
        self.epd << epd
        DoActions(self.epd.SetNumberX(0, 0xC0000000))
        self.off << 0

    def seekoffset(self, ptr):
        if not IsEUDVariable(ptr):
            raise RuntimeError("If you want to seek offset of EUDObject," \
                    "use seekepd(EPD(EUDObject))")

        epd, off = f_div(ptr, 4)
        epd += -0x58A364 // 4
        self.epd << epd
        DoActions(self.epd.SetNumberX(0, 0xC0000000))
        self.off << off

    @EUDMethod
    def read(self):
        ret = EUDVariable()
        ret << 0

        EUDSwitch(self.off)
        if EUDSwitchCase()(0):
            for i in range(8):
                Trigger(
                    conditions = MemoryXEPD(self.epd, Exactly, 2**i, 2**i),
                    actions = ret.AddNumber(2**i)
                )
            self.off += 1
            EUDBreak()
        if EUDSwitchCase()(1):
            for i in range(8):
                Trigger(
                    conditions = MemoryXEPD(self.epd, Exactly, 2**(i+8), 2**(i+8)),
                    actions = ret.AddNumber(2**i)
                )
            self.off += 1
            EUDBreak()
        if EUDSwitchCase()(2):
            for i in range(8):
                Trigger(
                    conditions = MemoryXEPD(self.epd, Exactly, 2**(i+16), 2**(i+16)),
                    actions = ret.AddNumber(2**i)
                )
            self.off += 1
            EUDBreak()
        if EUDSwitchCase()(3):
            for i in range(8):
                Trigger(
                    conditions = MemoryXEPD(self.epd, Exactly, 2**(i+24), 2**(i+24)),
                    actions = ret.AddNumber(2**i)
                )
            DoActions([self.epd.AddNumber(1), self.off.SetNumber(0)])
            EUDBreak()
        EUDEndSwitch()
        EUDReturn(ret)

    @EUDMethod
    def write(self, val):
        _acts = [Forward() for _ in range(4)]
        _offvals = [0xFF, 0xFF00, 0xFF0000, 0xFF000000]
        DoActions([SetMemory(_act+20, SetTo, 0) for _act in _acts])
        for i in range(8):
            RawTrigger(
                conditions = [
                    MemoryX(val.getValueAddr(), Exactly, 2**i, 2**i)
                ],
                actions = [
                    SetMemoryX(_acts[off]+20, Add, 2**(i+off*8), _offvals[off])
                    for off in range(4)
                ]
            )
        EUDSwitch(self.off)
        if EUDSwitchCase()(0):
            DoActions([
                _acts[0] << SetMemoryXEPD(self.epd, SetTo, 0, 0xFF),
                self.off.AddNumber(1)
            ])
            EUDBreak()
        if EUDSwitchCase()(1):
            DoActions([
                _acts[1] << SetMemoryXEPD(self.epd, SetTo, 0, 0xFF00),
                self.off.AddNumber(1)
            ])
            EUDBreak()
        if EUDSwitchCase()(2):
            DoActions([
                _acts[2] << SetMemoryXEPD(self.epd, SetTo, 0, 0xFF0000),
                self.off.AddNumber(1)
            ])
            EUDBreak()
        if EUDSwitchCase()(3):
            DoActions([
                _acts[3] << SetMemoryXEPD(self.epd, SetTo, 0, 0xFF000000),
                self.epd.AddNumber(1), self.off.SetNumber(0)
            ])
            EUDBreak()
        EUDEndSwitch()

    '''
    write_* functions do not write null byte
    '''
    @EUDMethod
    def write_str(self, srcptr):
        reader = EUDByteRW()
        reader.seekoffset(srcptr)

        if EUDInfLoop()():
            # read
            b = reader.read()

            # break
            EUDBreakIf(b == 0)

            # copy
            self.write(b)
        EUDEndInfLoop()

    @EUDMethod
    def write_strn(self, srcptr, n):
        reader = EUDByteRW()
        reader.seekoffset(srcptr)

        written = EUDVariable()
        written << 0
        if EUDWhile()(n >= 1):
            # read
            b = reader.read()

            # break
            EUDBreakIf(b == 0)

            # copy
            self.write(b)
            DoActions([
                n.SubtractNumber(1),
                written.AddNumber(1)
            ])
        EUDEndWhile()
        EUDReturn(written)

    @EUDMethod
    def write_strepd(self, srcepd):
        reader = EUDByteRW()
        reader.seekepd(srcepd)

        if EUDInfLoop()():
            # read
            b = reader.read()

            # break
            EUDBreakIf(b == 0)

            # copy
            self.write(b)
        EUDEndInfLoop()

    @EUDMethod
    def write_strnepd(self, srcepd, n):
        reader = EUDByteRW()
        reader.seekepd(srcepd)

        written = EUDVariable()
        written << 0
        if EUDWhile()(n >= 1):
            # read
            b = reader.read()

            # break
            EUDBreakIf(b == 0)

            # copy
            self.write(b)
            DoActions([
                n.SubtractNumber(1),
                written.AddNumber(1)
            ])
        EUDEndWhile()
        EUDReturn(written)

    @EUDMethod
    def write_decimal(self, number):
        skipper = [Forward() for _ in range(9)]
        ch = [0] * 10

        # Get digits
        for i in range(10):
            number, ch[i] = f_div(number, 10)
            if i != 9:
                EUDJumpIf(number == 0, skipper[i])

        # print digits
        for i in range(9, -1, -1):
            if i != 9:
                skipper[i] << NextTrigger()
            self.write(ch[i] + ord('0'))

    @EUDMethod
    def write_hex(self, number):
        ch = [0] * 8

        self.write(ord('0'))
        self.write(ord('x'))

        # Get digits
        for i in range(8):
            number, ch[i] = f_div(number, 16)

        # print digits
        for i in range(7, -1, -1):
            if EUDIf()(ch[i] <= 9):
                self.write(ch[i] + ord('0'))
            if EUDElse()():
                self.write(ch[i] + (ord('A') - 10))
            EUDEndIf()

    @EUDMethod
    def write_binary(self, number):
        self.write(ord('0'))
        self.write(ord('b'))

        for i in range(31, -1, -1):
            if i in [23, 15, 7]:
                self.write(ord(' '))
            if EUDIf()(MemoryX(number.getValueAddr(), Exactly, 2**i, 2**i)):
                self.write(ord('1'))
            if EUDElse()():
                self.write(ord('0'))
            EUDEndIf()

    @EUDMethod
    def write_bytehex(self, number):
        ch = [0] * 2

        # Get digits
        for i in range(2):
            number, ch[i] = f_div(number, 16)

        # print digits
        for i in range(1, -1, -1):
            if EUDIf()(ch[i] <= 9):
                self.write(ch[i] + ord('0'))
            if EUDElse()():
                self.write(ch[i] + (ord('A') - 10))
            EUDEndIf()

    @EUDMethod
    def write_memoryTable(self, offset, cnt):
        reader = EUDByteRW()
        reader.seekoffset(offset)

        written = EUDVariable()
        written << 0
        if EUDInfLoop()():
            EUDBreakIf(cnt == 0)

            b = reader.read()

            self.write_bytehex(b)
            self.write(ord(' '))

            DoActions(cnt.SubtractNumber(1))
        EUDEndInfLoop()

    @EUDMethod
    def write_bool(self, value):
        if EUDIfNot()(self.value == 0):
            self.write_strepd(EPDConstString("True"))
        if EUDElse()():
            self.write_strepd(EPDConstString("False"))
        EUDEndIf()

    @EUDMethod
    def write_u8(self, value):
        DoActions(value.SetNumberX(0, 0xFFFFFF00))
        skipper = [Forward() for _ in range(2)]
        digits = []

        for i in range(2):
            value, r = f_div(value, 10)
            digits.append(r)
            EUDJumpIf(value == 0, skipper[i])

        self.write(value + ord('0'))
        skipper[1] << NextTrigger()
        self.write(digits[1] + ord('0'))
        skipper[0] << NextTrigger()
        self.write(digits[0] + ord('0'))

    @EUDMethod
    def write_u16(self, value):
        DoActions(value.SetNumberX(0, 0xFFFF0000))
        skipper = [Forward() for _ in range(4)]
        digits = []

        for i in range(4):
            value, r = f_div(value, 10)
            digits.append(r)
            EUDJumpIf(value == 0, skipper[i])

        self.write(value + ord('0'))
        for i in range(3, -1, -1):
            skipper[i] << NextTrigger()
            self.write(digits[i] + ord('0'))

    @EUDMethod
    def write_u32(self, value):
        skipper = [Forward() for _ in range(9)]
        digits = []

        for i in range(9):
            value, r = f_div(value, 10)
            digits.append(r)
            EUDJumpIf(value == 0, skipper[i])

        self.write(value + ord('0'))
        for i in range(8, -1, -1):
            skipper[i] << NextTrigger()
            self.write(digits[i] + ord('0'))

    @EUDMethod
    def write_s8(self, value):
        if EUDIf()(value.ExactlyX(0x80, 0x80)):
            self.write(ord('-'))
            self.write_u8(-value)
        if EUDElse()():
            self.write_u8(value)
        EUDEndIf()

    @EUDMethod
    def write_s16(self, value):
        if EUDIf()(value.ExactlyX(0x8000, 0x8000)):
            self.write(ord('-'))
            self.write_u16(-value)
        if EUDElse()():
            self.write_u16(value)
        EUDEndIf()

    @EUDMethod
    def write_s32(self, value):
        if EUDIf()(value.ExactlyX(0x80000000, 0x80000000)):
            self.write(ord('-'))
            self.write_u32(-value)
        if EUDElse()():
            self.write_u32(value)
        EUDEndIf()

    @EUDMethod
    def write_STR_string(self, strId):
        strsect = f_dwread_epd(EPD(0x5993D4))
        self.write_str(strsect + f_dwread(strsect + strId*4))

    def write_f(self, fmt, *args):
        '''
        Parse formatted string with python (not in-game)
          and write it with EUDVariable or ConstExpr

        CAUTION: This does NOT make null end

        Available formats:
         - %H: hexadecimal value starts with 0x
         - %D: decimal value
         - %I8d: write_s8
         - %I16d: write_s16
         - %I32d: write_s32
         - %I8u: write_u8
         - %I16u: write_u16
         - %I32u: write_u32
         - %S: string with ptr
         - %E: string with epd
         - %C: single character

        Write %% to represent %
        '''
        # parse format and compare its argument count
        #   with args
        # ITEMS: list of tuples (format, arg)
        items = []
        pos = 0
        argidx = 0
        while pos < len(fmt):
            if '%' not in fmt[pos:]:
                items.append(('const', fmt[pos:]))
                break
            fmpos = fmt[pos:].index('%')

            # push conststr before %
            if fmpos > 0:
                items.append(('const', fmt[pos:pos+fmpos]))
                pos += fmpos

            # get argument
            if argidx >= len(args):
                raise RuntimeError("Mismatch on count between " \
                    "format string and argument counton write_f")
            curarg = args[argidx]
            if fmt[pos+1] == '%':
                items.append(('const', '%'))
            elif fmt[pos+1] == 'H':
                items.append(('H', curarg))
                argidx += 1
            elif fmt[pos+1] == 'D':
                items.append(('D', curarg))
                argidx += 1
            elif fmt[pos+1] == 'I':
                check = False
                for fs in ['8d', '16d', '32d', '8u', '16u', '32u']:
                    if fmt[pos+2:].startswith(fs):
                        items.append(('I' + fs, curarg))
                        pos += len(fs)
                        argidx += 1
                        check = True
                        break
                if not check:
                    print(fmt[pos:])
                    raise RuntimeError("Unable to parse {}".format(fmt))
            elif fmt[pos+1] == 'S':
                items.append(('S', curarg))
                argidx += 1
            elif fmt[pos+1] == 'E':
                items.append(('E', curarg))
                argidx += 1
            elif fmt[pos+1] == 'C':
                items.append(('C', curarg))
                argidx += 1
            else:
                print(fmt[pos:])
                raise RuntimeError("Unable to parse {}".format(fmt))
            pos += 2
        if len(args) != argidx:
            raise RuntimeError("Mismatch on count between " \
                "format string and argument count on write_f")

        # Due to %%, several const string could be
        #   located consecutively, so merge it
        merged_items = [items[0]]
        for fm, arg in items[1:]:
            if fm == 'const' and merged_items[-1][0] == 'const':
                merged_items[-1] = (merged_items[-1][0],
                        merged_items[-1][1] + arg)
            else:
                merged_items.append((fm, arg))

        # Short constants are written with bytes, otherwise use EPDConstString
        func_matches = {
            'I8d': self.write_s8,
            'I16d': self.write_s16,
            'I32d': self.write_s32,
            'I8u': self.write_u8,
            'I16u': self.write_u16,
            'I32u': self.write_u32
        }
        for fm, arg in merged_items:
            if fm == 'const':
                if len(arg) == 1:
                    self.write(ord(arg))
                else:
                    self.write_strepd(EPDConstString(arg))
            elif fm == 'H':
                self.write_hex(arg)
            elif fm == 'D':
                self.write_decimal(arg)
            elif fm == 'S':
                self.write_str(arg)
            elif fm == 'E':
                self.write_strepd(arg)
            elif fm == 'C':
                self.write(arg)
            else:
                func_matches[fm](arg)
