from eudplib import *
from .staticstruct import StaticStruct

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
        return f_dwread_epd(self.contents + index)

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

        cpmoda, cond = Forward(), Forward()
        dstepdp = end
        srcepdp = end-1
        VProc([dstepdp, srcepdp, contents, index], [
            SetMemory(cpmoda, SetTo, 1),
            SetMemory(loopc+8, SetTo, -1),
            dstepdp.QueueAddTo(EPD(cpmoda)),
            srcepdp.QueueAssignTo(EPD(0x6509B0)),
            contents.QueueAddTo(EPD(loopc+8)),
            index.QueueAddTo(EPD(loopc+8))
        ])

        # while (cp != &(contents+index-1))
        if EUDWhileNot()(loopc << Memory(cpmoda, Exactly, 0)):
            cpmod = f_dwread_cp(0)
            cpmoda << cpmod.getDestAddr()

            VProc(cpmod, [
                SetMemory(cpmoda, Add, -1),
                SetMemory(0x6509B0, Add, -1)
            ])
        EUDEndInfLoop()

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
