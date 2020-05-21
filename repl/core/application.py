from eudplib import *

from ..base.referencetable import ReferenceTable
from ..utils import EPDConstString
from .appcommand import AppCommandN, runAppCommand
from .appmanager import get_app_manager
from .appmethod import AppMethodN, AppMethod, AppMethod_writerParam

class _indexPair:
    def __init__(self, items = None):
        if items is None:
            items = dict()
        self.items = items
        self.size = len(items)

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
    apps = []
    def __init__(cls, name, bases, dct):
        ''' Fill methods, commands, members '''
        super().__init__(name, bases, dct)

        # build methods and members, basically from parent class
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
            if isinstance(v, AppCommandN):
                assert k not in total_dict or isinstance(total_dict[k], AppCommandN), \
                        "Conflict on attribute - %s.%s" % (name, k)
                if k in commands:
                    commands.replace(k, v)
                else:
                    commands.append(k, v)
                v.initialize(cls)
                total_dict[k] = v
            elif callable(v) or isinstance(v, AppMethodN):
                assert not (k[:2] == k[-2:] == "__"), \
                        "Illegal method - %s.%s" % (name, k)
                assert k not in total_dict or isinstance(total_dict[k], AppMethodN), \
                        "Conflict on attribute - %s.%s" % (name, k)
                if not isinstance(v, AppMethodN):
                    v = AppMethod(v)
                setattr(cls, k, v)
                if k in methods:
                    # Overriding AppMethod
                    v.initialize(cls, methods[k][0], methods.getValue(k))
                    methods.replace(k, v)
                else:
                    v.initialize(cls, len(methods))
                    methods.append(k, v)
                total_dict[k] = v
            else:
                assert k not in total_dict or total_dict[k] == 'Other', \
                        "Conflict on attribute - %s.%s" % (name, k)
                total_dict[k] = 'Other'

        # fields for the cases that a child newly defined field
        if pcls == object or id(cls.fields) != id(pcls.fields):
            for f in cls.fields:
                if isinstance(f, str):
                    k, typ = f, None
                else:
                    k, typ = f
                assert k not in total_dict, \
                        "Conflict on attribute - %s.%s" % (name, k)
                fields.append(k, typ)
                total_dict[k] = 'F'

        cls._total_dict_ = total_dict
        cls._methods_ = methods
        cls._commands_ = commands
        cls._fields_ = fields
        cls._allocated_ = False
        _Application_Metaclass.apps.append(cls)

class ApplicationInstance:
    '''
    Mimic object for application instance, used in AppMethod.
    It supports field access and method invocation.

    Typically _absolute is False.
    Leaf AppMethods are called, set by current instance.
    Otherwise, their absolute address are used.
    It would applied into calling methods from superclasses.
    '''

    # reserved keywords
    _attributes_ = ['_cls', '_absolute', 'getReference_epd']


    def __init__(self, cls = None):
        if cls:
            self._cls = cls
            self._absolute = True
        else:
            self._cls = Application
            self._absolute = False

    def getReference_epd(self, member):
        '''
        Get reference for instance member

        self.var << 1                     # self.var is 1
        v = self.getReference_epd('var')  # get reference for self.var
        f_dwwrite_epd(v, 12)
        Logger.format("%D", self.var)     # self.var becomes 12

        Traditional EUDVariable can be referenced as EPD(v.getValueAddr())
        '''
        attrid, attrtype = self._cls._fields_[member]
        return get_app_manager().cur_members._epd + (18 * attrid + 348 // 4)

    def __getattr__(self, name):
        if name in self._cls._commands_:
            raise RuntimeError("You should not invoke AppCommand directly")
        elif name in self._cls._methods_:
            i, v = self._cls._methods_[name]
            if not self._absolute:
                return v.apply()
            else:
                return v.applyAbsolute()
        elif name in self._cls._fields_:
            attrid, attrtype = self._cls._fields_[name]
            attr = get_app_manager().cur_members.get(attrid)
            if attrtype:
                return attrtype.cast(attr)
            else:
                return attr
        raise AttributeError("Application '%s' has no attribute '%s'" % (self._cls, name))

    def __setattr__(self, name, value):
        if name in ApplicationInstance._attributes_:
            super().__setattr__(name, value)
        elif name in self._cls._fields_:
            attrid, attrtype = self._cls._fields_[name]
            get_app_manager().cur_members.set(attrid, value)
        else:
            raise AttributeError("Application '%s' has no attribute '%s'" % (self._cls, name))

# default application
class Application(metaclass=_Application_Metaclass):
    # deafult field - cmd_output_epd
    # if it is not 0, the reason of failure on
    #    runAppCommand() is written into cmd_output_epd.
    fields = ["cmd_output_epd"]

    def onInit(self):
        self.cmd_output_epd = 0

    def onDestruct(self):
        pass

    def onChat(self, offset):
        runAppCommand(
            offset,
            self.cmd_output_epd
        )

    def onResume(self):
        ''' onResume() called exactly once after forward application was closed '''
        pass

    def loop(self):
        ''' loop() called exactly once in every frame '''
        pass

    @AppMethod_writerParam
    def print(self, writer):
        ''' called once in a frame that invoked requestUpdate '''
        writer.write(0)

    @classmethod
    def getSuper(cls):
        parent = cls.__mro__[1]
        assert parent != object

        return ApplicationInstance(parent)

    @classmethod
    def allocate(cls):
        if not cls._allocated_:
            if cls.__mro__[1] != object:
                cls.__mro__[1].allocate()

            # allocate methods
            methodarray = []
            for mtd in cls._methods_.orderedValues():
                mtd.allocate()
                methodarray.append(mtd.getFuncPtr())
            cls._methodarray_ = EUDVArray(len(methodarray))(methodarray)
            cls._methodarray_epd_ = EPD(cls._methodarray_)

            # allocate commands
            cmdtable = ReferenceTable(key_f=EPDConstString)
            for name, cmd in cls._commands_.orderedItems():
                cmd.allocate()
                cmdtable.AddPair(name, cmd.getCmdPtr())

            cls._cmdtable_ = cmdtable
            cls._allocated_ = True

    @classmethod
    def addCommand(cls, name, cmd):
        assert isinstance(cmd, AppCommandN), "CMD (%s) must be callable or AppCommand" % cmd

        if cls._allocated_:
            # case allocated
            #   - unable to replace, just append only
            #   - initialize and allocate
            assert name not in cls._total_dict_, \
                    "Please avoid to use '%s' as the command name on class %s," \
                    "or add it before allocation of the class" % (name, cls.__name__)
            cls._commands_.append(name, cmd)
            cmd.initialize(cls)
            cls._total_dict_[name] = cmd

            cmd.allocate()
            cls._cmdtable_.AddPair(name, cmd.getCmdPtr())
        else:
            # case not allocated
            #   - replace or add
            #   - just initialize
            assert name not in cls._total_dict_ or isinstance(cls._total_dict_[name], AppCommandN), \
                    "Conflict on attribute - %s.%s" % (cls.__name__, name)
            if name in cls._commands_:
                cls._commands_.replace(name, cmd)
            else:
                cls._commands_.append(name, cmd)
            cmd.initialize(cls)
            cls._total_dict_[name] = cmd
