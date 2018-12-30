from eudplib import *
from command import EUDCommand
from utils import *
from encoder import ReadNumber, ReadName

_writer = EUDByteRW()

@EUDFunc
def decItem_StringDecimal(offset, name, val):
    _writer.seekoffset(offset)
    _writer.write_strepd(name)
    _writer.write_strepd(EPD(makeText(': ')))
    _writer.write_decimal(val)
    _writer.write(0)

@EUDFunc
def decItem_StringHex(offset, name, val):
    _writer.seekoffset(offset)
    _writer.write_strepd(name)
    _writer.write_strepd(EPD(makeText(': ')))
    _writer.write_hex(val)
    _writer.write(0)

@EUDFunc
def decItem_String(offset, name, val):
    _writer.seekoffset(offset)
    _writer.write_strepd(name)
    _writer.write(0)

class ReferenceTable(EUDObject):
    '''
    Same with EUDArray with contents
        size(=N), key 1, value 1, key 2, value 2, ..., key N, value N
    However, these key-value pair are lazily collected.

    key_f transforms key before registered.
    rt = ReferenceTable(key_transformer = makeText)
    rt.AddPair("Hello", 3) # transforms "Hello" to EPD(Db())

    value_f works similar to key_f
    '''
    def __init__(self,
            initdict=[], 
            ref_by = [],
            key_f = lambda k:k,
            value_f = lambda v:v
        ):
        super().__init__()
        self._dict = []
        self.key_f = key_f
        self.value_f = value_f

        # Added on parents lazily
        self._ref_by = ref_by

        # Check the object called Evaluate() at least once
        self._addedToParents = False

        # list of tuples, [(k1, v1), (k2, v2), ... ]
        for k, v in initdict:
            self.AddPair(k, v)

    def AddPair(self, key, value):
        # duplicate check
        key = self.key_f(key)
        for k, v in self._dict:
            if k == key:
                raise RuntimeError
        value = self.value_f(value)
        ep_assert(IsConstExpr(key), 'Invalid item {}'.format(key))
        ep_assert(IsConstExpr(value), 'Invalid item {}'.format(value))
        self._dict.append((key, value))

    def AddPairLazily(self, key, value):
        from eudplib.core.allocator.payload import phase, PHASE_COLLECTING
        assert phase == PHASE_COLLECTING

        # duplicate check
        self.AddPair(key, value)

    def Evaluate(self):
        # Collection phase
        if not self._addedToParents:
            for parent, key in self._ref_by:
                parent.AddPairLazily(key, self)
            self._addedToParents = True
        return super().Evaluate()

    def DynamicConstructed(self):
        return True

    def GetDataSize(self):
        return 4 + 8 * len(self._dict)

    def CollectDependency(self, emitbuffer):
        for key, value in self._dict:
            if key is not int:
                emitbuffer.WriteDword(key)
            if value is not int:
                emitbuffer.WriteDword(value)

    def WritePayload(self, emitbuffer):
        emitbuffer.WriteDword(len(self._dict))
        for key, value in self._dict:
            emitbuffer.WriteDword(key)
            emitbuffer.WriteDword(value)

@EUDTypedFunc([None, None, EUDFuncPtr(2, 1), None], [None])
def SearchTable(key, table_epd, compareFunc, retval_epd):
    size = f_dwread_epd(table_epd)
    k, v = table_epd + 1, table_epd + 2
    if EUDInfLoop()():
        EUDBreakIf(size == 0)
        if EUDIf()(compareFunc(key, f_dwread_epd(k)) == 0): # Caution: 0
            f_dwwrite_epd(retval_epd, f_dwread_epd(v))
            EUDReturn(1)
        EUDEndIf()
        DoActions([
            size.SubtractNumber(1),
            k.AddNumber(2),
            v.AddNumber(2),
        ])
    EUDEndInfLoop()
    EUDReturn(0)

@EUDFunc
def PrintTable(table_epd):
    f_simpleprint('size:', f_dwread_epd(table_epd))
    f_dbepd_print(f_dwread_epd(table_epd+1))
    f_simpleprint(hptr(f_dwread_epd(table_epd+2)))
    # f_dbepd_print(table_epd+3)

    # f_simpleprint(hptr(f_dwread_epd(table_epd+4)))
