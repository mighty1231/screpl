from eudplib import *
from ..utils import f_raiseError

'''
DbPool and VarPool allocates buffer as Db and EUDVarible respectively.
Its concept is based on stack. Allocated buffer should be freed with reversed order.
'''
class DbPool:
    def __init__(self, size):
        # EUDVArray: 72 byte for each variable
        self.size = size
        self.data = EUDArray([0 for _ in range(size)])
        self.cur_epd = EUDVariable(EPD(self.data))
        self.alloc_cnt = EUDVariable(0)
        self.alloc_history = EUDArray(200)

    @EUDMethod
    def alloc_epd(self, sz):
        ret = EUDVariable()
        ret << self.cur_epd

        # push on history stack
        self.alloc_history[self.alloc_cnt] = self.cur_epd
        self.alloc_cnt += 1
        self.cur_epd += sz
        if EUDIf()(self.cur_epd >= (EPD(self.data) + self.size)):
            f_raiseError("SC_REPL ERROR - DbPool.Alloc()")
        EUDEndIf()
        EUDReturn(ret)

    @EUDMethod
    def free_epd(self, epd):
        # pop on history stack
        self.alloc_cnt -= 1
        last_epd = self.alloc_history[self.alloc_cnt]
        if EUDIfNot()(epd == last_epd):
            f_raiseError("SC_REPL ERROR - DbPool.Free()")
        EUDEndIf()
        self.cur_epd << last_epd

class VarPool:
    def __init__(self, size):
        # EUDVArray: 72 byte for each variable
        self.size = size
        self.data = EUDVArray(size)([0 for _ in range(size)])
        self.cur_ptr = EUDVariable(self.data._value)
        self.alloc_cnt = EUDVariable(0)
        self.alloc_history = EUDArray(40)

    @EUDTypedMethod([None], [EUDVArray(0)])
    def alloc(self, sz):
        ret = EUDVariable()
        ret << self.cur_ptr

        # push on history stack
        self.alloc_history[self.alloc_cnt] = self.cur_ptr
        self.alloc_cnt += 1
        self.cur_ptr += sz * 72
        if EUDIf()(self.cur_ptr >= (self.data._value + 72*self.size)):
            f_raiseError("SC_REPL ERROR - VarPool.Alloc()")
        EUDEndIf()
        EUDReturn(ret)

    @EUDMethod
    def free(self, ptr):
        # pop on history stack
        self.alloc_cnt -= 1
        last_ptr = self.alloc_history[self.alloc_cnt]
        if EUDIfNot()(ptr == last_ptr):
            f_raiseError("SC_REPL ERROR - VarPool.Free()")
        EUDEndIf()
        self.cur_ptr << last_ptr
