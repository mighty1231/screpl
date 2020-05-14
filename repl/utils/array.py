from eudplib import *
from .staticstruct import StaticStruct

class Array(StaticStruct):
    fields = [
        'max_size',
        'size',
        'contents', # EPD(EUDArray())
        'begin',
        'end'
    ]

    @staticmethod
    def build(max_size, initvals = None):
        size = EUDVariable(0)

        if initvals:
            initvals += [0 for _ in range(max_size - len(initvals))]
            contents = EPD(EUDArray(initvals))
        else:
            contents = EPD(EUDArray(max_size))
        begin = EUDVariable(EPD(contents))
        end = EUDVariable(EPD(contents) + max_size)

        return (max_size, size, contents, begin, end)

    @EUDMethod
    def at(self, index):
        return f_dwread_epd(self.contents + index)

    @EUDMethod
    def insert(self, index, value):
        contents = self.contents
        size = self.size
        end = self.end

        # @TODO iteration

    @EUDMethod
    def delete(self, index):
        '''
        delete item with index
        '''
        contents = self.contents
        size = self.size
        end = self.end

        # index,   index+1, ..., size-2, size-1
        # index+1, index+2, ..., size-1
        dst = contents + index
        src = dst + 1
        f_repmovsd_epd(dst, src, size-index-1)
        self.size = size - 1
        self.end = end - 1

    @EUDMethod
    def contains(self, item):
        cond1, cond2 = Forward(), Forward()
        SeqCompute([
            (EPD(cond2 + 4), SetTo, self.begin),
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
