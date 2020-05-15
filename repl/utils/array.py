from eudplib import *
from .staticstruct import StaticStruct
from .debug import f_raiseError

class Array(StaticStruct):
    fields = [
        'max_size',
        'size',
        'contents', # EPD(EUDArray())
        'end'
    ]

    @staticmethod
    def build(max_size, initvals = None):
        size = EUDVariable(0)

        if initvals:
            size = len(initvals)
            initvals += [0 for _ in range(max_size - len(initvals))]
            contents = EPD(EUDArray(initvals))
        else:
            size = 0
            contents = EPD(EUDArray(max_size))

        return (max_size, size, contents, contents+size)

    @EUDMethod
    def at(self, index):
        if EUDIf()(index >= self.size):
            f_raiseError("IndexError: array index out of range")
        EUDEndIf()
        return f_dwread_epd(self.contents + index)

    @EUDMethod
    def append(self, value):
        size = self.size
        end = self.end
        if EUDIf()(size == self.max_size):
            f_raiseError("BufferOverflowError: array size exceeds max_size")
        EUDEndIf()

        f_dwwrite_epd(end, value)

        self.end = end + 1
        self.size = size + 1

    @EUDMethod
    def insert(self, index, value):
        '''
        insert item on index
                index index+1 index+2 ... size-1  size
        before: v_i   v_(i+1) v_(i+2) ... v_(s-1) (end)
        after:  value v_i     v_(i+1) ... v_(s-2) v_(s-1) (end)
        '''
        contents = self.contents
        size = self.size
        end = self.end

        if EUDIf()(size == self.max_size):
            f_raiseError("BufferOverflowError: array size exceeds max_size")
        EUDEndIf()
        if EUDIfNot()(index <= size):
            f_raiseError("IndexError: array index out of range")
        EUDEndIf()

        cpmoda, loopc = Forward(), Forward()
        dstepdp = end
        srcepdp = end-1
        VProc([dstepdp, srcepdp, contents, index], [
            SetMemory(cpmoda, SetTo, 1),
            dstepdp.QueueAddTo(EPD(cpmoda)),
            srcepdp.QueueAssignTo(EPD(0x6509B0)),
            contents.QueueAssignTo(EPD(loopc+8)),
            index.QueueAddTo(EPD(loopc+8))
        ])

        # while (src != &(contents+index))
        if EUDWhileNot()(loopc << Memory(cpmoda, Exactly, 0)):
            # cpmod = *src
            cpmod = f_dwread_cp(0)
            cpmoda << cpmod.getDestAddr()

            # *(--dst) = --cpmod
            VProc(cpmod, [
                SetMemory(cpmoda, Add, -1),
                SetMemory(0x6509B0, Add, -1)
            ])
        EUDEndWhile()

        f_setcurpl2cpcache()
        f_dwwrite_epd(contents + index, value)
        self.size = size + 1
        self.end = end + 1

    @EUDMethod
    def delete(self, index):
        '''
        delete item with index
        before: index,   index+1, ..., size-2, size-1
        after:  index+1, index+2, ..., size-1
        '''
        contents = self.contents
        size = self.size
        end = self.end

        if EUDIf()(index >= size):
            f_raiseError("IndexError: array index out of range")
        EUDEndIf()

        dst = contents + index
        src = dst + 1
        f_repmovsd_epd(dst, src, size-index-1)
        self.size = size - 1
        self.end = end - 1

    @EUDMethod
    def contains(self, item):
        cond1, cond2 = Forward(), Forward()
        SeqCompute([
            (EPD(cond2 + 4), SetTo, self.contents),
            (EPD(cond2 + 8), SetTo, item),
            (EPD(cond1 + 8), SetTo, self.end)
        ])
        if EUDInfLoop()():
            # break if *ptr == end
            EUDBreakIf(cond1 << Memory(cond2 + 4, Exactly, 0))

            # if (*ptr == item)
            if EUDIf()(cond2 << Memory(0, Exactly, 0)):
                EUDReturn(1)
            EUDEndIf()

            # ptr++
            DoActions(SetMemory(cond2 + 4, Add, 1))
        EUDEndInfLoop()
        EUDReturn(0)

    def values(self):
        '''
        iterate over values in array
        '''
        blockname = 'arrayloop'
        EUDCreateBlock(blockname, self)

        epd = self.contents
        end = self.end
        cond = Forward()
        SeqCompute([(EPD(cond + 8), SetTo, end)])
        EUDWhileNot()(cond << epd.Exactly(0))

        yield f_dwread_epd(epd)
        EUDSetContinuePoint()
        epd += 1
        EUDEndWhile()

        ep_assert(
            EUDPopBlock(blockname)[1] is self,
            'arrayloop mismatch'
        )
