'''
REPLStruct
similar to EUDStruct, but specialized to REPL::

    class MyStruct(REPLStruct):
        fields = ['a']

    s1 = MyStruct(a=4)
    v = EUDVariable()
    v << s1
    print(v) # has same value with s

    s2 = MyStruct.cast(v)
    s2.a += 5
    print(s.a) # 5
'''
from eudplib import *

class _REPLStructMetaclass(type):

    # pylint: disable=no-value-for-parameter
    fieldmap = {}
    def __new__(mcl, name, bases, dct):
        cls = super().__new__(mcl, name, bases, dct)
        fields = {}
        for index, member in enumerate(dct['fields']):
            if isinstance(member, str):
                name, ty = member, None
            else:
                name, ty = member
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
