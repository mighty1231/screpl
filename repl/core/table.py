from eudplib import *

class ReferenceTable(EUDObject):
    '''
    Same with EUDArray with contents
        size(=N), key 1, value 1, key 2, value 2, ..., key N, value N
    However, these key-value pair are lazily collected.

    key_f transforms key before registered.
    rt = ReferenceTable(key_transformer = makeEPDText)
    rt.AddPair("Hello", 3) # transforms "Hello" to EPD(Db())

    value_f works similar to key_f
    '''
    def __init__(self,
            initdict=[], 
            ref_by = [],
            key_f = lambda k:k,
            value_f = lambda v:v,
            sortkey_f = lambda k,v:0,
        ):
        super().__init__()
        self._dict = []
        self.key_f = key_f
        self.value_f = value_f
        self.sortkey_f = sortkey_f

        # Save transformed objects
        self._keys = []
        self._values = []

        # Added on parents lazily
        self._ref_by = ref_by

        # Check the object called Evaluate() at least once
        self._addedToParents = False

        # list of tuples, [(k1, v1), (k2, v2), ... ]
        for k, v in initdict:
            self.AddPair(k, v)

    def AddPair(self, key, value):
        # duplicate check
        for k, v in self._dict:
            if k == key:
                raise RuntimeError('Duplicate of key {}'.format(k))

        # Record original key & value + transformed key & value
        key_tr = self.key_f(key)
        value_tr = self.value_f(value)

        ep_assert(IsConstExpr(key_tr), 'Invalid key {}'.format(key))
        ep_assert(IsConstExpr(value_tr), 'Invalid value {}'.format(value))

        self._keys.append(key_tr)
        self._values.append(value_tr)
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
        for key_tr in self._keys:
            if key_tr is not int:
                emitbuffer.WriteDword(key_tr)
        for value_tr in self._values:
            if value_tr is not int:
                emitbuffer.WriteDword(value_tr)

    def WritePayload(self, emitbuffer):
        emitbuffer.WriteDword(len(self._dict))
        tuples = sorted(zip(self._keys, self._values, self._dict),
            key=lambda kvd:self.sortkey_f(kvd[2][0], kvd[2][1]))
        for key, value, item in tuples:
            emitbuffer.WriteDword(key)
            emitbuffer.WriteDword(value)

    @staticmethod
    def Iter(table_epd, func):
        '''
        func receives i, key_epd, value_epd and do something
        '''
        i = EUDVariable()
        k_epd = table_epd + 1
        v_epd = table_epd + 2
        i << 0
        if EUDInfLoop()():
            EUDBreakIf(MemoryEPD(table_epd, AtMost, i))
            func(i, k_epd, v_epd)
            DoActions([
                i.AddNumber(1),
                k_epd.AddNumber(2),
                v_epd.AddNumber(2)
            ])
        EUDEndInfLoop()

    @staticmethod
    def GetSize(table_epd):
        return f_dwread_epd(table_epd)

@EUDTypedFunc([None, None, EUDFuncPtr(2, 1), None], [None])
def SearchTable(key, table_epd, compareFunc, retval_epd):
    def func(i, k, v):
        if EUDIf()(compareFunc(key, f_dwread_epd(k)) == 0): # Caution: 0
            f_dwwrite_epd(retval_epd, f_dwread_epd(v))
            EUDReturn(1)
        EUDEndIf()
    ReferenceTable.Iter(table_epd, func)
    EUDReturn(0)

@EUDFunc
def SearchTableInv(value, table_epd, retval_epd):
    def func(i, k, v):
        if EUDIf()(MemoryEPD(v, Exactly, value)): # Caution: 0
            f_dwwrite_epd(retval_epd, f_dwread_epd(k))
            EUDReturn(1)
        EUDEndIf()
    ReferenceTable.Iter(table_epd, func)
    EUDReturn(0)
