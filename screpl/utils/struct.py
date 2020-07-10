'''
REPLStruct
similar to EUDStruct, but specialized to REPL::

    class MyStruct(REPLStruct):
        fields = ['a']

    s1 = MyStruct(a=4)
    v = EUDVariable()
    v << s1
    print(v) # has same value with s1

    s2 = MyStruct.cast(v)
    s2.a += 5
    print(s1.a) # 5
'''
from eudplib import *

class _REPLStructMetaclass(type):

    # pylint: disable=no-value-for-parameter
    fieldmap = {}
    def __new__(mcl, name, bases, dct):
        cls = super().__new__(mcl, name, bases, dct)
        fields = {}
        for index, field in enumerate(dct['fields']):
            if isinstance(field, str):
                name, ty = field, None
            else:
                name, ty = field
                if ty is selftype:
                    ty = cls
            assert name not in ['_epd', '_from', '_value'], \
                    "attribute '%s' is reserved" % name
            fields[name] = (index, ty)
        _REPLStructMetaclass.fieldmap[cls] = fields
        return cls

    def __call__(cls, _from):
        if IsConstExpr(_from):
            baseobj = _from
        else:
            baseobj = EUDVariable()
            baseobj << _from
        instance = super().__call__(baseobj)
        instance._epd = EPD(instance)

        return instance

    def empty_pointer(cls):
        instance = super().__call__(EUDVariable())
        instance._epd = EUDVariable()
        return instance

    def initialize_with(cls, *args):
        from eudplib.core.eudstruct.vararray import EUDVArrayData
        fields = _REPLStructMetaclass.fieldmap[cls]
        assert len(args) == len(fields)

        baseobj = EUDVArrayData(len(args))(args)
        return cls(baseobj)

    def getfield(cls, instance, name):
        attrid, attrtype = _REPLStructMetaclass.fieldmap[cls][name]

        # same as EUDVArray.get(attrid)
        value = EUDVariable()
        vtproc = Forward()
        nptr = Forward()
        a0, a2 = Forward(), Forward()

        SeqCompute([
            (EPD(vtproc + 4), SetTo, instance + 72 * attrid),
            (EPD(a0 + 16), SetTo, instance._epd + (18 * attrid + 344 // 4)),
            (EPD(a2 + 16), SetTo, instance._epd + (18 * attrid + 1)),
        ])

        vtproc << RawTrigger(
            nextptr=0,
            actions=[
                a0 << SetDeaths(0, SetTo, EPD(value.getValueAddr()), 0),
                a2 << SetDeaths(0, SetTo, nptr, 0),
            ]
        )

        nptr << NextTrigger()
        if attrtype:
            return attrtype.cast(value)
        return value

    def setfield(cls, instance, name, value):
        attrid, attrtype = _REPLStructMetaclass.fieldmap[cls][name]

        # same as EUDVArray.set(attrid, value)
        a0, t = Forward(), Forward()
        SeqCompute([
            (EPD(a0 + 16), SetTo, instance._epd + (18 * attrid + 348 // 4)),
            (EPD(a0 + 20), SetTo, value),
        ])
        t << RawTrigger(
            actions=[
                a0 << SetDeaths(0, SetTo, 0, 0),
            ]
        )

    def cpy(cls, dest, src):
        """Copy field values, from dest to src"""
        if type(src) is type(dest):
            src_epd = src._epd
        elif IsEUDVariable(src):
            src_epd = EPD(src)
        else:
            raise ValueError("Type mismatch")


        fieldn = len(type(dest).fields)
        attrid = EUDVariable()
        vtproc = Forward()
        nptr = Forward()
        a0, a2 = Forward(), Forward()

        attrid << 0
        SeqCompute([
            (EPD(vtproc + 4), SetTo, src),
            (EPD(a0 + 16), SetTo, src_epd + 344 // 4),
            (EPD(a2 + 16), SetTo, src_epd + 1),
            (EPD(a0 + 20), SetTo, dest._epd + 348 // 4),
        ])
        if EUDInfLoop()():
            EUDBreakIf(attrid >= fieldn)

            vtproc << RawTrigger(
                nextptr=0,
                actions=[
                    a0 << SetDeaths(0, SetTo, 0, 0),
                    a2 << SetDeaths(0, SetTo, nptr, 0),
                ]
            )

            nptr << NextTrigger()

            DoActions([
                attrid.AddNumber(1),
                SetMemory(vtproc + 4, Add, 72),
                SetMemory(a0 + 16, Add, 18),
                SetMemory(a2 + 16, Add, 18),
                SetMemory(a0 + 20, Add, 18),
            ])
        EUDEndInfLoop()

class REPLStruct(ExprProxy, metaclass=_REPLStructMetaclass):
    fields = []

    @classmethod
    def cast(cls, _from):
        return cls(_from)

    def __getattr__(self, name):
        try:
            return type(self).getfield(self, name)
        except KeyError:
            return super().__getattr__(name)

    def __setattr__(self, name, value):
        try:
            type(self).setfield(self, name, value)
        except KeyError:
            assert name in ['_epd', '_value']
            super().__setattr__(name, value)

    def __lshift__(self, other):
        if IsEUDVariable(self):
            # move pointer
            if isinstance(other, REPLStruct):
                self << unProxy(other)
                self._epd << other._epd
            elif IsEUDVariable(other):
                self << other
                self._epd << EPD(other)
            else:
                raise ValueError
        else:
            # copy
            type(self).cpy(self, other)
