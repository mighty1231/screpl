from eudplib import *

from screpl.utils.debug import f_raise_error
from screpl.utils.string import f_memcmp_epd
from screpl.utils.struct import REPLStruct

@cachedfunc
def MaximumCircularBuffer(elem_type):
    class _DataClass(REPLStruct):
        fields = [
            "count",
            "max_size",
            "content_epd", # EPD of EUDArray
        ]

        # @staticmethod
        # def construct(max_size, ty_=None):
        #     obj = MaximumCircularBuffer.initialize_with(0,
        #                                                 max_size,
        #                                                 EUDArray(max_size))
        #     obj.type = ty_
        #     return obj

        # @EUDMethod
        # def push(self, item):
        #     count = self.count
        #     max_size = self.max_size
        #     content_epd = self.content_epd

        #     quot, rem = f_div(count, max_size)
        #     f_dwwrite_epd(content_epd + rem, item)

        #     self.count = count + 1

        @classmethod
        def construct_w_empty(cls, values):
            assert isinstance(values, list)
            obj = cls.initialize_with(0,
                                      len(values),
                                      EPD(EUDArray(values)))
            return obj

        def empty(self):
            return self.count == 0

        def last(self):
            """returns the last element of the buffer"""
            ret = self._last()
            return elem_type.cast(ret)

        @EUDMethod
        def _last(self):
            count = self.count
            if EUDIf()(count == 0):
                f_raise_error("MaximumCircularBuffer.last(): buffer is empty")
            EUDEndIf()

            quot, rem = f_div(count-1, self.max_size)
            return f_dwread_epd(self.content_epd + rem)

        def push_and_get_reference(self):
            """Increase count and return the reference of item"""
            count = self.count
            max_size = self.max_size
            content_epd = self.content_epd

            quot, rem = f_div(count, max_size)

            self.count = count + 1
            return content_epd + rem

        def iter(self, iter_f):
            count = self.count
            if EUDIf()(count == 0):
                EUDReturn()
            EUDEndIf()

            max_size = self.max_size
            content_epd = self.content_epd
            quot, rem = f_div(count, max_size)

            # iteration
            idx = EUDTernary(quot==0)(0)(rem)
            if EUDInfLoop()():
                # read content_epd and apply iter_f
                iter_f(f_dwread_epd(content_epd + idx))

                idx += 1
                Trigger(
                    conditions=(idx == max_size),
                    actions=idx.SetNumber(0))
                EUDBreakIf(idx == rem)
            EUDEndInfLoop()

    return _DataClass

class ResultEntry(REPLStruct):
    fields = [
        "start_tick",
        "end_tick",
        "cond_count",
        "cond_bools_epd", # EPD(EUDArray)
        "cond_values_epd", # EPD(EUDArray)
    ]

    @staticmethod
    def construct():
        return ResultEntry.initialize_with(0, 0, 0,
                                           EPD(EUDArray(16)),
                                           EPD(EUDArray(16)))

    @EUDMethod
    def update(self, count, bools_epd, values_epd):
        """Compare the entry with new data and update

        If they're different, return 1.
        otherwise update tick and returns 0
        """
        s_count = self.cond_count
        s_bools_epd = self.cond_bools_epd
        s_values_epd = self.cond_values_epd

        if EUDIfNot()(s_count == count):
            EUDReturn(1)
        EUDEndIf()

        if EUDIfNot()(f_memcmp_epd(s_bools_epd, bools_epd, count) == 0):
            EUDReturn(1)
        EUDEndIf()
        if EUDIfNot()(f_memcmp_epd(s_values_epd, values_epd, count) == 0):
            EUDReturn(1)
        EUDEndIf()

        self.end_tick = f_getgametick()
        EUDReturn(0)
