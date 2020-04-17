from eudplib import *

from .appmethod import AppMethod_print
from .appcommand import runAppCommand
from ...utils import EPDConstString
from ..referencetable import ReferenceTable

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
            sorted(self.items.items(), key = lambda item:item[1][0])))

    def getValue(self, key):
        return self.items[key][1]

    def __len__(self):
        return self.size

    def __contains__(self, key):
        return key in self.items

    def __getitem__(self, key):
        return self.items[key]

class _Application_Metaclass(type):
    def __init__(cls, name, bases, dct):
        '''
        Fill methods, commands, members
        '''
        from . import _AppMethod, _AppCommand, AppMethod

        super().__init__(name, bases, dct)


        # build methods and members
        # basically from parents
        pcls = cls.__mro__[1]
        if pcls == object:
            methods = _indexPair()
            commands = _indexPair()
            fields = _indexPair()
            total_dict = {k:None for k in ApplicationInstance._attributes_}
        else:
            methods = pcls._methods_.copy()
            commands = pcls._commands_.copy()
            fields = pcls._fields_.copy()
            total_dict = pcls._total_dict_.copy()

        # methods and commands
        for k, v in dct.items():
            if isinstance(v, _AppCommand):
                assert k not in total_dict or isinstance(total_dict[k], _AppCommand), \
                        "Conflict on attribute - class %s attr %s" % (name, k)
                if commands.hasKey(k):
                    commands.replace(k, v)
                else:
                    commands.append(k, v)
                total_dict[k] = v
            elif callable(v) or isinstance(v, _AppMethod):
                assert not (k[:2] == k[-2:] == "__"), \
                        "Illegal method - class %s attr %s" % (name, k)
                assert k not in total_dict or isinstance(total_dict[k], _AppMethod), \
                        "Conflict on attribute - class %s attr %s" % (name, k)
                if not isinstance(v, _AppMethod):
                    v = AppMethod(v)
                setattr(cls, k, v)
                if methods.hasKey(k):
                    # Overriding AppMethod
                    v.setParent(methods.getValue(k))
                    methods.replace(k, v)
                else:
                    methods.append(k, v)
                total_dict[k] = v
            else:
                assert k not in total_dict or total_dict[k] == 'Other', \
                        "Conflict on attribute - class %s attr %s" % (name, k)
                total_dict[k] = 'Other'

        # fields for the cases that a child newly defined field
        if pcls != object:
            print('p', pcls.fields)
        print('c', cls.fields)
        print('=============')
        if pcls == object or id(cls.fields) != id(pcls.fields):
            for f in cls.fields:
                if isinstance(f, str):
                    k, typ = f, None
                else:
                    k, typ = f
                assert not commands.hasKey(f), "A key %s is already defined as a command" % f
                assert not methods.hasKey(f), "A key %s is already defined as a method" % f
                assert not fields.hasKey(f), "A key %s is already defined as a field" % f
                fields.append(k, typ)
                total_dict[k] = 'F'

        cls._total_dict_ = total_dict
        cls._methods_ = methods
        cls._commands_ = commands
        cls._fields_ = fields
        cls._initialized_ = False

        print("New Application name", name)
        print(total_dict)
        print('------------')

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
        self._ivarr = EUDVArray(12345).cast(self._memberptr)
        self._mvarr = EUDVArray(12345).cast(self._methodptr)
        self._cmdtable_epd = EUDVariable()

    def _update(self):
        # assert IsEUDVariable(unProxy(self._ivarr))
        unProxy(self._ivarr) << self._memberptr
        self._ivarr._epd << EPD(self._memberptr)
        unProxy(self._mvarr) << self._methodptr
        self._mvarr._epd << EPD(self._methodptr)

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
        raise AttributeError

    def __setattr__(self, name, value):
        if name in ApplicationInstance._attributes_:
            super().__setattr__(name, value)
        elif name in self._cls._fields_:
            attrid, attrtype = self._cls._fields_[name]
            self._ivarr.set(attrid + 1, value)
        else:
            print(name, value, self._cls._fields_.items)
            raise AttributeError

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

    @AppMethod_print
    def print(self, writer):
        ''' called once in a frame that invoked requestUpdate '''
        pass

    @classmethod
    def initialize(cls):
        if not cls._initialized_:
            if cls.__mro__[1] != object:
                cls.__mro__[1].initialize()

            # Initialize methods
            methodarray = []
            for i, mtd in enumerate(cls._methods_.orderedValues()):
                mtd.initialize(cls, i)
                methodarray.append(mtd.getFuncPtr())
            cls._methodarray_ = EUDVArray(len(methodarray))(methodarray)

            # initialize commands
            cmdtable = ReferenceTable(key_f=EPDConstString)
            for name, (i, cmd) in enumerate(cls._commands_.orderedItems()):
                cmd.initialize(cls)
                cmdtable.AddPair(name, cmd.getCmdPtr())

            cls._cmdtable_ = cmdtable
            cls._initialized_ = True

    @classmethod
    def addCommand(cls, name, command):
        from . import _AppCommand
        assert isinstance(command, _AppCommand)
        assert not cls._commands_.hasKey(name)
        command.initialize(cls)
        cls._commands_.append(name, command)
        cls._cmdtable_.AddPair(name, command.getCmdPtr())
