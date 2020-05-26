from eudplib import *

class ReferenceTable(EUDObject):
    """Dynamic object to store key-value pair

    Same as EUDArray with contents:

    ===== ======== ===== ======= ===== ======= === =========  =======
    index 0        1     2       3     4       ...   2N-1     2N
    value size(=N) key1  value1  key2  value2  ...   keyN     valueN
    ===== ======== ===== ======= ===== ======= === =========  =======

    However, these key-value pair are lazily collected.

    key_f transforms key before registered::

        rt = ReferenceTable(key_transformer = EPDConstString)
        rt.add_pair("Hello", 3) # transforms "Hello" to EPD(Db())

    value_f works similar to key_f
    """
    def __init__(self,
                 initdict=None,
                 ref_by=None,
                 key_f=lambda k: k,
                 value_f=lambda v: v,
                 sortkey_f=lambda k, v: 0):
        super().__init__()

        if not initdict:
            initdict = []
        if not ref_by:
            ref_by = []

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
            self.add_pair(k, v)

    def add_pair(self, key, value):
        # duplicate check
        for k, _ in self._dict:
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

    def add_pair_lazily(self, key, value):
        from eudplib.core.allocator.payload import phase, PHASE_COLLECTING
        assert phase == PHASE_COLLECTING

        # duplicate check
        self.add_pair(key, value)

    def Evaluate(self):
        # Collection phase
        if not self._addedToParents:
            for parent, key in self._ref_by:
                parent.add_pair_lazily(key, self)
            self._addedToParents = True
        return super().Evaluate()

    def DynamicConstructed(self):
        return True

    def GetDataSize(self):
        return 4 + 8 * len(self._dict)

    def CollectDependency(self, pbuffer):
        for key_tr in self._keys:
            if key_tr is not int:
                pbuffer.WriteDword(key_tr)
        for value_tr in self._values:
            if value_tr is not int:
                pbuffer.WriteDword(value_tr)

    def WritePayload(self, pbuffer):
        pbuffer.WriteDword(len(self._dict))
        tuples = sorted(zip(self._keys, self._values, self._dict),
            key=lambda kvd:self.sortkey_f(kvd[2][0], kvd[2][1]))
        for key, value, item in tuples:
            pbuffer.WriteDword(key)
            pbuffer.WriteDword(value)

    @staticmethod
    def iter_table(table_epd, func):
        '''
        func receives i, key_epd, value_epd and do something
        '''
        if not IsEUDVariable(table_epd):
            _table_epd = EUDVariable()
            _table_epd << table_epd
        else:
            _table_epd = table_epd
        i = EUDVariable()
        k_epd = _table_epd + 1
        v_epd = _table_epd + 2
        i << 0
        if EUDInfLoop()():
            EUDBreakIf(MemoryEPD(_table_epd, AtMost, i))
            func(i, k_epd, v_epd)
            DoActions([
                i.AddNumber(1),
                k_epd.AddNumber(2),
                v_epd.AddNumber(2)
            ])
        EUDEndInfLoop()

    @staticmethod
    def get_size(table_epd):
        return f_dwread_epd(table_epd)

@EUDTypedFunc([None, None, EUDFuncPtr(2, 1), None], [None])
def search_table(key, table_epd, compare_func, retval_epd):
    def func(i, k, v):
        if EUDIf()(compare_func(key, f_dwread_epd(k)) == 0): # Caution: 0
            f_dwwrite_epd(retval_epd, f_dwread_epd(v))
            EUDReturn(1)
        EUDEndIf()
    ReferenceTable.iter_table(table_epd, func)
    EUDReturn(0)

@EUDFunc
def search_table_inv(value, table_epd, retval_epd):
    def func(i, k, v):
        if EUDIf()(MemoryEPD(v, Exactly, value)): # Caution: 0
            f_dwwrite_epd(retval_epd, f_dwread_epd(k))
            EUDReturn(1)
        EUDEndIf()
    ReferenceTable.iter_table(table_epd, func)
    EUDReturn(0)
