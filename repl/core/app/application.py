from eudplib import *

from ...utils import EPDConstString
from ..referencetable import ReferenceTable
from .appmethod import _AppMethod
from .appcommand import AppCommand

class _indexPair:
    def __init__(self, items = None):
        if items is None:
            items = dict()
        self.items = items
        self.size = len(items)

    def debugPrint(self):
        print("- _indexPair id {} dictid {}--".format(id(self), id(self.items)))
        for i, t in enumerate(self.items):
            print(' {}: {}'.format(i, t))
        print("---")

    def hasKey(self, key):
        return key in self.items

    def replace(self, key, new_value):
        idx, old_value = self.items[key]
        self.items[key] = idx, new_value

    def append(self, key, val = None):
        assert key not in self.items, "Key duplicates: {}".format(key)
        self.items[key] = (self.size, val)
        self.size += 1

    def copy(self):
        # Just copy field, not instance
        return _indexPair(self.items.copy())

    def orderedValues(self):
        return list(map(lambda iv:iv[1], \
            sorted(self.items.values(), key = lambda pair:pair[0])))

    def orderedItems(self):
        return list(map(lambda item:(item[0], item[1][1]), \
            sorted(self.items.items(), key = lambda pair:item[1][0])))

    def __len__(self):
        return self.size

    def __getitem__(self, key):
        return self.items[key]

class AppClassStruct:
    def __init__(self, cls, methods):
        assert isinstance(methods, _indexPair)

        self.cls = cls
        self.methods = methods
        self.data = EUDVArray(len(methods))([])

    def getVArrayData(self):
        return self.data

    def invoke(self, name, instance):

class _Application_Metaclass(type):
    def __init__(cls, name, bases, dct):
        '''
        Fill methods, commands, members
        '''
        super().__init__(name, bases, dct)

        print("New Application name", name)

        # build methods and members
        # basically from parents
        pcls = cls.__mro__[1]
        if pcls == object:
            methods = _indexPair()
            commands = _indexPair()
            fields = _indexPair()
        else:
            methods = pcls._methods_.copy()
            commands = pcls._commands_.copy()
            fields = pcls._fields_.copy()

        # methods and commands
        # @TODO key comparison (versus override)
        for k, v in dct.items():
            assert k not in ApplicationInstance._attributes_, \
                    "You should not use key %s as a member" % k
            if isinstance(v, AppCommand):
                assert not methods.hasKey(k), "A key %s is already defined as a method" % k
                assert not fields.hasKey(k), "A key %s is already defined as a field" % k
                if commands.hasKey(k):
                    commands.replace(k, v)
                else:
                    commands.append(k, v)
            elif callable(v):
                if not isinstance(v, _AppMethod):
                    v = AppMethod(v)
                    assert isinstance(v, _AppMethod)
                assert not (k[:2] == k[-2:] == "__"), \
                        "method %s should not be defined" % k
                assert not commands.hasKey(k), "A key %s is already defined as a command" % k
                assert not fields.hasKey(k), "A key %s is already defined as a field" % k
                setattr(cls, k, v)
                if methods.hasKey(k):
                    methods.replace(k, v)
                else:
                    methods.append(k, v)

        # fields for the cases that a child newly defined field
        if pcls == object or id(cls.fields) != id(pcls.fields):
            for f in cls.fields:
                assert not commands.hasKey(f), "A key %s is already defined as a command" % f
                assert not methods.hasKey(f), "A key %s is already defined as a method" % f
                assert not fields.hasKey(f), "A key %s is already defined as a field" % f
                fields.append(f)
                # @TODO field type conversion

        # collect commands
        cmdtable = ReferenceTable(key_f=EPDConstString)
        for name, cmd in commands.orderedItems():
            cmdtable.AddPair(name, cmd)

        cls._methods_ = methods
        cls._methodarray_ = EUDVArray(len(methods))(list(map(
                lambda am:am.getFuncPtr(), methods.orderedValues())))
        cls._commands_ = commands
        cls._cmdtable_ = cmdtable
        cls._fields_ = fields
        cls._initialized_ = False

class ApplicationInstance:
    '''
    instance: EUDVArray
      item #0: method pointers of class
      item #1: instance field [0]
      item #i: instance field [i+1]
    '''
    _attributes_ = ['_cls', '_memberptr', '_methodptr',
            '_ivarr', '_mvarr', '_cmdtable_epd', '_update']
    def __init__(self):
        self._cls = None
        self._memberptr = EUDVariable()
        self._methodptr = EUDVariable()
        self._ivarr, self._mvarr = EUDVArray(0)(), EUDVArray(0)()
        self._cmdtable_epd = EUDVariable()

    def _update(self):
        self._ivarr << self._memberptr
        self._mvarr << self._methodptr

    def __getattr__(self, name):
        if name in self._cls._commands_:
            raise RuntimeError("You should not invoke AppCommand directly")
        elif name in self._cls._methods_:
            i, v = self._cls._methods_[name]
            return v.apply(self)
            # return self._methodptr.get(i)
        elif name in self._cls._fields_:
            attrid, attrtype = self._cls._fields_[name]
            attr = self._ivarr.get(attrid + 1)
            if attrtype:
                return attrtype.cast(attr)
            else:
                return attr
        return super().__getattr__(name)

    def __setattr__(self, name, value):
        if name in self._cls._fields_:
            attrid, attrtype = self._cls._fields_[name]
            self._ivarr.set(attrid + 1, value)
        elif name in ApplicationInstance._attributes_:
            super().__setattr__(key, value)
        else:
            raise AttributeError("class %s key %s" % \
                    (self._cls.__name__, name))

# default application
class Application(metaclass=_Application_Metaclass):
    fields = ["cmd_output_epd"]
    def init(self):
        self.cmd_output_epd = 0

    def destruct(self):
        pass

    def chatCallback(self, offset):
        runAppCommand(
            offset,
            self.cmd_output_epd
        )

    def loop(self):
        ''' loop() called exactly once in every frame '''
        pass

    def print(self, writer):
        ''' called once in a frame that invoked requestUpdate '''
        pass

    @classmethod
    def initialize(cls):
        if not cls._initialized_:
            for i, mtd in enumerate(cls._methods_.orderedValues()):
                mtd.initialize(cls, i)
            for i, cmd in enumerate(cls._commands_.orderedValues()):
                cmd.initialize(cls)
            cls._initialized_ = True

    @classmethod
    def addCommand(cls, name, command):
        assert isinstance(command, AppCommand)
        assert not cls._commands_.hasKey(name)
        command.initialize(cls)
        cls._commands_.append(name, command)
        cls._cmdtable_.AddPair(name, command)
