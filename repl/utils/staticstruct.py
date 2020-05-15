'''
StaticStruct
similar to EUDStruct, but specialized to REPL

class MyStruct(StaticStruct):
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

class _StaticStruct_Metaclass(type):
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
        _StaticStruct_Metaclass.fieldmap[cls] = fields
        return cls

    def __call__(cls, *args, **kwargs):
        from eudplib.core.eudstruct.vararray import EUDVArrayData
        if '_from' in kwargs:
            # cast
            assert args == [] and len(kwargs) == 1
            _from = kwargs['_from']
            if IsConstExpr(_from):
                baseobj = _from
            else:
                baseobj = EUDVariable()
                baseobj << _from
        else:
            # statically construct
            args = cls.build(*args, **kwargs)
            fields = _StaticStruct_Metaclass.fieldmap[cls]
            assert isinstance(args, tuple) and len(args) == len(fields)

            baseobj = EUDVArrayData(len(args))(args)

        instance = super().__call__(baseobj)
        instance._epd = EPD(instance)

        return instance

    def getfield(cls, instance, name):
        attrid, attrtype = _StaticStruct_Metaclass.fieldmap[cls][name]

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
        attrid, attrtype = _StaticStruct_Metaclass.fieldmap[cls][name]

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

class StaticStruct(ExprProxy, metaclass=_StaticStruct_Metaclass):
    fields = []

    @staticmethod
    def build(*args):
        '''
        Tuple used on initialize variables on EUDVArray

        class SomeStruct(StaticStruct):
            fields = ['a', 'b']
            @staticmethod
            def build(a, b = 4):
                return (a, b)

        Then, you can construct SomeStruct instance, like
            SomeStruct(10) or SomeStruct(4, b=30)
        
        Invoked on _StaticStruct_Metaclass.__call__
        '''
        return args

    @classmethod
    def cast(cls, _from):
        return cls(_from=_from)

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
