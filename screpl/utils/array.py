from eudplib import *

from . import debug
from . import pool
from . import struct

_pool = pool.DbPool(100000)

@EUDFunc
def _default_compare(a, b):
    # return 1 if a < b
    if EUDIfNot()(a >= b):
        EUDReturn(1)
    EUDEndIf()
    EUDReturn(0)

@EUDFunc
def _swap(array, i, j):
    '''
    Used on REPLArray.sort (quicksort algorithm)
    '''
    array = REPLArray.cast(array)
    contents = array.contents
    i_epd = contents + i
    j_epd = contents + j
    tmp = f_dwread_epd(j_epd)
    f_dwwrite_epd(j_epd, f_dwread_epd(i_epd))
    f_dwwrite_epd(i_epd, tmp)

@EUDFunc
def _partition(array, left, right, comp):
    '''
    Used on REPLArray.sort (quicksort algorithm)
    '''
    array = REPLArray.cast(array)
    comp = EUDFuncPtr(2, 1).cast(comp)
    i, j = EUDCreateVariables(2)
    breakc = Forward()

    pivot = array.at(right)
    i << left - 1
    j << left
    SeqCompute([(EPD(breakc + 8), SetTo, right)])
    if EUDInfLoop()():
        EUDBreakIf(breakc << j.AtLeast(0))
        if EUDIfNot()(comp(array.at(j), pivot) == 0):
            i += 1
            _swap(array, i, j)
        EUDEndIf()
        j += 1
    EUDEndInfLoop()
    _swap(array, i + 1, right)
    EUDReturn(i + 1)

class REPLArray(struct.REPLStruct):
    fields = [
        'max_size',
        'size',
        'contents', # EPD(EUDArray())
        'end'
    ]

    @staticmethod
    def construct(max_size, initvals=None):
        if initvals:
            size = len(initvals)
            initvals += [0 for _ in range(max_size - size)]
            contents = EPD(EUDArray(initvals))
        else:
            size = 0
            contents = EPD(EUDArray(max_size))

        return REPLArray.initialize_with(max_size, size, contents, contents+size)

    @staticmethod
    def allocate(max_size):
        contents = _pool.alloc_epd(max_size)
        instance = REPLArray.initialize_with(0, 0, 0, 0)
        instance.max_size = max_size
        instance.contents = contents
        instance.end = contents
        return instance

    @EUDMethod
    def free(self):
        '''
        Can be freed if the instance is initialized with allocate()
        '''
        _pool.free_epd(self.contents)

    @EUDMethod
    def at(self, index):
        if EUDIf()(index >= self.size):
            debug.f_raise_error("IndexError: array index out of range")
        EUDEndIf()
        return f_dwread_epd(self.contents + index)

    @EUDMethod
    def append(self, value):
        size = self.size
        end = self.end
        if EUDIf()(size == self.max_size):
            debug.f_raise_error("BufferOverflowError: array size exceeds max_size")
        EUDEndIf()

        f_dwwrite_epd(end, value)

        self.end = end + 1
        self.size = size + 1

    @EUDMethod
    def clear(self):
        self.size = 0
        self.end = self.contents

    @EUDMethod
    def pop(self):
        """Removes and returns item at last"""
        end = self.end
        size = self.size
        if EUDIf()(size == 0):
            debug.f_raise_error("IndexError: pop from empty array")
        EUDEndIf()

        end -= 1
        ret = f_dwread_epd(end)
        self.end = end
        self.size = size-1
        EUDReturn(ret)

    @EUDMethod
    def insert(self, index, value):
        """Inserts item on index

        ====== ===== ======= ======= === ========= ======== ======
        insert index index+1 index+2 ... size-1    size     size+1
        ------ ----- ------- ------- --- --------- -------- ------
        before v_i   v_(i+1) v_(i+2) ... v_(s-1)   (end)
        after  value v_i     v_(i+1) ... v_(s-2)   v_(s-1)  (end)
        ====== ===== ======= ======= === ========= ======== ======
        """
        contents = self.contents
        size = self.size
        end = self.end

        if EUDIf()(size == self.max_size):
            debug.f_raise_error("BufferOverflowError: array size exceeds max_size")
        EUDEndIf()
        if EUDIfNot()(index <= size):
            debug.f_raise_error("IndexError: array index out of range")
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
        """Deletes item with index

        ====== ======= ======= === ====== ======
        before index   index+1 ... size-2 size-1
        after  index+1 index+2 ... size-1 (empty)
        ====== ======= ======= === ====== ======
        """
        contents = self.contents
        size = self.size
        end = self.end

        if EUDIf()(index >= size):
            debug.f_raise_error("IndexError: array index out of range")
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

    @EUDMethod
    def index(self, item):
        """Returns the smallest index which has item.

        If there is no such index, returns -1
        """
        cond1, cond2 = Forward(), Forward()
        SeqCompute([
            (EPD(cond2 + 4), SetTo, self.contents),
            (EPD(cond2 + 8), SetTo, item),
            (EPD(cond1 + 8), SetTo, self.end)
        ])
        ret = EUDVariable()
        ret << 0
        if EUDInfLoop()():
            # break if *ptr == end
            EUDBreakIf(cond1 << Memory(cond2 + 4, Exactly, 0))

            # if (*ptr == item)
            if EUDIf()(cond2 << Memory(0, Exactly, 0)):
                EUDReturn(ret)
            EUDEndIf()

            # ptr++
            DoActions([
                SetMemory(cond2 + 4, Add, 1),
                ret.AddNumber(1)
            ])
        EUDEndInfLoop()
        EUDReturn(-1)

    def sort(self, comp=None):
        if comp is None:
            comp = _default_compare
        self._sort(comp)

    @EUDTypedMethod([EUDFuncPtr(2, 1)], [])
    def _sort(self, comp):
        '''
        comp: EUDFuncN that accepts two elements in the range as arguments,
        and returns a value convertible to bool. The value returned indicates
        whether the element passed as first argument is considered to go
        before the second in the specific strict weak ordering it defines.
        The function shall not modify any of its arguments.
        This can either be a function pointer or a function object.
        '''
        size = self.size

        # non-recursive quicksort
        stack = REPLArray.allocate(size * 2)
        stack.append(0)
        stack.append(size-1)
        if EUDWhileNot()(stack.size == 0):
            right = stack.pop()
            left = stack.pop()

            # unsigned comparison
            EUDContinueIf(left >= right)

            index = _partition(self, left, right, comp)

            # left part
            # prevent index be -1, due to unsigned comparison
            if EUDIfNot()(index == 0):
                stack.append(left)
                stack.append(index-1)
            EUDEndIf()

            # right part
            stack.append(index+1)
            stack.append(right)
        EUDEndWhile()
        stack.free()

    def values(self):
        """iterate over values in array

        Example::

            array = REPLArray.construct(5, [1, 2, 3, 2, 1])
            for v in array.values():
                f_printf("%D", v)

            # prints 1 2 3 2 1 on each lines
        """
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

@cachedfunc
def create_refarray(cls, empty_constructor):
    """Create a reference array class"""
    assert issubclass(cls, struct.REPLStruct)

    class _(struct.REPLStruct):
        fields = [
            'max_size',
            'size',
            'contents', # EPD(EUDArray())
            'end'
        ]

        @staticmethod
        def construct(max_size, initvals=None):
            if not initvals:
                initvals = []
            size = len(initvals)
            values = initvals + [empty_constructor()
                                 for _ in range(max_size - size)]
            contents = EPD(EUDArray(values))

            return _.initialize_with(max_size, size, contents,
                                             contents + size)

        @EUDTypedMethod([None], [cls])
        def at(self, index):
            if EUDIf()(index >= self.size):
                debug.f_raise_error("IndexError: array index out of range")
            EUDEndIf()
            return f_dwread_epd(self.contents + index)

        @EUDTypedMethod([], [cls])
        def push_and_getref(self):
            size = self.size
            end = self.end
            if EUDIf()(size == self.max_size):
                debug.f_raise_warning(
                    "BufferOverflowError: array size exceeds max_size")
                EUDReturn(0)
            EUDEndIf()

            self.end = end + 1
            self.size = size + 1

            EUDReturn(f_dwread_epd(end))

        @EUDTypedMethod([], [cls])
        def pop(self):
            """Removes and returns item at last"""
            end = self.end
            size = self.size
            if EUDIf()(size == 0):
                debug.f_raise_error("IndexError: pop from empty array")
            EUDEndIf()

            end -= 1
            ret = f_dwread_epd(end)
            self.end = end
            self.size = size-1
            return ret

        @EUDTypedMethod([None], [cls])
        def insert_and_getref(self, index):
            """Inserts item on index

            ====== ===== ======= ======= === ========= ======== ======
            insert index index+1 index+2 ... size-1    size     size+1
            ------ ----- ------- ------- --- --------- -------- ------
            before v_i   v_(i+1) v_(i+2) ... v_(s-1)   (end)
            after  value v_i     v_(i+1) ... v_(s-2)   v_(s-1)  (end)
            ====== ===== ======= ======= === ========= ======== ======
            """
            contents = self.contents
            size = self.size
            end = self.end

            if EUDIf()(size == self.max_size):
                debug.f_raise_warning(
                    "BufferOverflowError: array size exceeds max_size")
                EUDReturn(0)
            EUDEndIf()
            if EUDIfNot()(index <= size):
                debug.f_raise_warning("IndexError: array index out of range")
                EUDReturn(0)
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
            self.size = size + 1
            self.end = end + 1

            EUDReturn(f_dwread_epd(contents + index))

        @EUDMethod
        def delete(self, index):
            """Deletes item with index

            ====== ======= ======= === ====== ======
            before index   index+1 ... size-2 size-1
            after  index+1 index+2 ... size-1 (empty)
            ====== ======= ======= === ====== ======
            """
            contents = self.contents
            size = self.size
            end = self.end

            if EUDIf()(index >= size):
                debug.f_raise_error("IndexError: array index out of range")
            EUDEndIf()

            dst = contents + index
            src = dst + 1
            f_repmovsd_epd(dst, src, size-index-1)
            self.size = size - 1
            self.end = end - 1

        @EUDTypedMethod([EUDTypedFuncPtr([cls, cls], [None])], [])
        def sort(self, comp):
            '''
            comp: EUDFuncN that accepts two elements in the range as arguments,
            and returns a value convertible to bool. The value returned indicates
            whether the element passed as first argument is considered to go
            before the second in the specific strict weak ordering it defines.
            The function shall not modify any of its arguments.
            This can either be a function pointer or a function object.
            '''
            size = self.size

            # non-recursive quicksort
            stack = _.allocate(size * 2)
            stack.append(0)
            stack.append(size-1)
            if EUDWhileNot()(stack.size == 0):
                right = stack.pop()
                left = stack.pop()

                # unsigned comparison
                EUDContinueIf(left >= right)

                index = _partition(self, left, right, comp)

                # left part
                # prevent index be -1, due to unsigned comparison
                if EUDIfNot()(index == 0):
                    stack.append(left)
                    stack.append(index-1)
                EUDEndIf()

                # right part
                stack.append(index+1)
                stack.append(right)
            EUDEndWhile()
            stack.free()

        def values(self):
            """iterate over values in array"""
            blockname = 'arrayloop'
            EUDCreateBlock(blockname, self)

            epd = self.contents
            end = self.end
            cond = Forward()
            SeqCompute([(EPD(cond + 8), SetTo, end)])
            EUDWhileNot()(cond << epd.Exactly(0))

            yield cls.cast(f_dwread_epd(epd))
            EUDSetContinuePoint()
            epd += 1
            EUDEndWhile()

            ep_assert(
                EUDPopBlock(blockname)[1] is self,
                'arrayloop mismatch'
            )

    return _
