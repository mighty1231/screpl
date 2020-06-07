from eudplib import *

from screpl.utils.conststring import EPDConstString
from screpl.utils.referencetable import ReferenceTable

from . import appcommand
from . import appmethod

class _IndexPair:
    def __init__(self, items = None):
        if items is None:
            items = dict()
        self.items = items
        self.size = len(items)

    def replace(self, key, new_value):
        idx, _ = self.items[key]
        self.items[key] = idx, new_value

    def append(self, key, val = None):
        if key in self.items:
            raise ValueError("Key duplicates: {}".format(key))
        self.items[key] = (self.size, val)
        self.size += 1

    def copy(self):
        # Just copy field, not instance
        return _IndexPair(self.items.copy())

    def ordered_values(self):
        return list(map(lambda iv:iv[1], \
            sorted(self.items.values(), key = lambda pair:pair[0])))

    def ordered_items(self):
        return list(map(lambda item:(item[0], item[1][1]), \
            sorted(self.items.items(), key = lambda item:item[1][0])))

    def get_value(self, key):
        return self.items[key][1]

    def __len__(self):
        return self.size

    def __contains__(self, key):
        return key in self.items

    def __getitem__(self, key):
        return self.items[key]

class _ApplicationMetaclass(type):
    """Magically modify Application

    1. Change default methods to AppMethods.
    2. Register AppCommands and AppMethods.
    3. Read 'field' attribute to construct field.
    """
    apps = []
    def __init__(cls, name, bases, dct):
        """ Fill methods, commands, members """
        super().__init__(name, bases, dct)

        # build methods and members, basically from parent class
        pcls = cls.__mro__[1]
        if pcls == object:
            methods = _IndexPair()
            commands = _IndexPair()
            fields = _IndexPair()
            total_dict = {k:None for k in ApplicationInstance._attributes_}
        else:
            methods = pcls._methods_.copy()
            commands = pcls._commands_.copy()
            fields = pcls._fields_.copy()
            total_dict = pcls._total_dict_.copy()

        # iterate over attributes on class
        # register AppMethodN and AppCommandN
        # for k, v in dct.items():
        for key in sorted(dct.keys()):
            value = dct[key]
            if isinstance(value, appcommand.AppCommandN):
                if (key in total_dict
                        and not isinstance(
                            total_dict[key],
                            appcommand.AppCommandN)):
                    raise ValueError("Attribute name conflict %s.%s"
                                     % (name, key))
                if key in commands:
                    # replace AppCommand from parent class
                    commands.replace(key, value)
                else:
                    commands.append(key, value)
                value.initialize(cls)
                total_dict[key] = value
            elif callable(value) or isinstance(value, appmethod.AppMethodN):
                if key[:2] == key[-2:] == "__":
                    raise ValueError(
                        "You cannot define special python methods - %s.%s"
                        % (name, key))
                if (key in total_dict
                        and not isinstance(
                            total_dict[key],
                            appmethod.AppMethodN)):
                    raise ValueError("Attribute name conflict %s.%s"
                                     % (name, key))
                if not isinstance(value, appmethod.AppMethodN):
                    value = appmethod.AppMethod(value)
                setattr(cls, key, value)
                if key in methods:
                    # override AppMethodN
                    pidx, pmethod = methods[key]
                    value.initialize(cls, pidx, pmethod)
                    methods.replace(key, value)
                else:
                    value.initialize(cls, len(methods))
                    methods.append(key, value)
                total_dict[key] = value
            else:
                if (key in total_dict
                        and total_dict[key] != 'Other'):
                    raise ValueError("Attribute name conflict %s.%s"
                                     % (name, key))
                total_dict[key] = 'Other'

        # fields for the cases that a child newly defined field
        if pcls == object or id(cls.fields) != id(pcls.fields):
            for field in cls.fields:
                if isinstance(field, str):
                    fname, ftype = field, None
                else:
                    fname, ftype = field
                if fname in total_dict:
                    raise ValueError("Attribute name conflict %s.%s"
                                     % (name, fname))
                fields.append(fname, ftype)
                total_dict[fname] = 'F'

        cls._total_dict_ = total_dict
        cls._methods_ = methods
        cls._commands_ = commands
        cls._fields_ = fields
        cls._allocated_ = False
        _ApplicationMetaclass.apps.append(cls)

class ApplicationInstance:
    """Mimic object for application instance.

    ApplicationInstance is a pure python object to manage attributes of
    Application instance, which is on the foreground of application stack,
    instead of 'self' parameter.

    It enables following:

    1. Invoke its AppMethods.

    2. Access and modify its fields.

    3. Used as the first parameter (self) for AppCommand and AppMethod.

    Typically _absolute is False. This case methods and commands are
    referenced relative to the foreground app and its original class type.
    Otherwise, using _cls attribute, their absolute functions are referenced.

    It enables successful AppMethod overriding::

        # class definitions
        class MyApp1(Application):
            def func(self):
                f_printf("hello")

        class MyApp2(MyApp1):
            def func(self):
                f_printf("hi")

        # appmanager loaded MyApp2 object as a foreground app
        #  - app stack
        #    [1]: MyApp2
        #    [0]: REPL

        # relative call (MyApp2 is on foreground)
        in1 = ApplicationInstance()
        in1.func() # prints hi

        # absolute call
        in2 = ApplicationInstance(MyApp1)
        in2.func() # prints hello
    """

    # reserved keywords
    _attributes_ = ['_cls', '_absolute', '_manager',
                    'get_reference_epd', 'run_command']

    def __init__(self, manager, cls = None):
        self._manager = manager
        if cls:
            self._cls = cls
            self._absolute = True
        else:
            self._cls = Application
            self._absolute = False

    def get_reference_epd(self, member):
        """Returns address for current foreground app instance member

        For example::

            class MyApp(Application):
                fields = ['var']

                def some_method(self):
                    self.var = 1

                    # get reference for self.var
                    var_ref = self.get_reference_epd('var')
                    f_dwwrite_epd(var_ref, 12)

                    # now self.var becomes 12

        Traditional EUDVariable can be referenced as EPD(var.getValueAddr())
        """
        attrid, _ = self._cls._fields_[member]
        return (self._manager.cur_members._epd
                + (18*attrid + 348//4))

    def run_command(self, address):
        if self._absolute:
            raise ValueError("Running command absolutely is not supported")
        appcommand.run_app_command(self._manager, address)

    def __getattr__(self, name):
        if name in self._cls._commands_:
            raise RuntimeError("You should not invoke AppCommand directly")
        elif name in self._cls._methods_:
            _, v = self._cls._methods_[name]
            if not self._absolute:
                return v.apply(self._manager)
            else:
                return v.applyAbsolute()
        elif name in self._cls._fields_:
            attrid, attrtype = self._cls._fields_[name]
            attr = self._manager.cur_members.get(attrid)
            if attrtype:
                return attrtype.cast(attr)
            else:
                return attr
        raise AttributeError("Application '%s' has no attribute '%s'"
                             % (self._cls, name))

    def __setattr__(self, name, value):
        if name in ApplicationInstance._attributes_:
            super().__setattr__(name, value)
        elif name in self._cls._fields_:
            attrid, _ = self._cls._fields_[name]
            self._manager.cur_members.set(attrid, value)
        else:
            raise AttributeError("Application '%s' has no attribute '%s'"
                                 % (self._cls, name))

class Application(metaclass=_ApplicationMetaclass):
    """Basic structure that defines the way to interact with user"""

    fields = []

    def on_init(self):
        """Called once when the application initialized and goes foreground"""

    def on_destruct(self):
        """Called when the application is going to be destructed"""

    def on_chat(self, address):
        """Called when the super user has chatted something.

        Arguments:
            address (EUDVariable): address of chat from super user.
        """
        self.run_command(address) # pylint: disable=no-member

    def on_resume(self):
        """Called exactly once after newly started app is destructed
        and the app became to be foreground again"""

    def loop(self):
        """Called exactly once in every frame"""

    @appmethod.AppMethodWithMainWriter
    def print(self, writer):
        """Called once in a frame that invoked request_update"""
        writer.write(0)

    @classmethod
    def get_super(cls):
        """Get superclass instance

        May be used for overriding AppMethodN object. Usage::

            def on_init(self):
                self.my_var = 3
                self.get_super().on_init()
        """
        parent = cls.__mro__[1]
        if parent == object:
            raise ValueError("The class %s has no superclass" % cls.__name__)

        return ApplicationInstance(parent)

    @classmethod
    def allocate(cls, manager):
        """Constructs the array for commands and methods on the app.

        Before the AppManager start the appliction, it should be called.
        """
        if not cls._allocated_:
            cls._allocated_ = True
            cls.manager = manager

            if cls != Application:
                parent_cls = cls.__mro__[1]
                assert issubclass(parent_cls, Application)
                parent_cls.allocate(manager) # pylint: disable=no-member

            # allocate methods
            methodarray = []
            for mtd in cls._methods_.ordered_values():
                mtd.allocate(manager)
                methodarray.append(mtd.get_func_ptr())
            cls._methodarray_ = EUDVArray(len(methodarray))(methodarray)
            cls._methodarray_epd_ = EPD(cls._methodarray_)

            # allocate commands
            cmdtable = ReferenceTable(key_f=EPDConstString)
            for name, cmd in cls._commands_.ordered_items():
                cmd.allocate(manager)
                cmdtable.add_pair(name, cmd.get_cmd_ptr())

            cls._cmdtable_ = cmdtable

    @classmethod
    def add_command(cls, name, cmd):
        """Add AppCommand for application"""
        if not isinstance(cmd, appcommand.AppCommandN):
            raise ValueError("AppCommand (%s) must be callable or AppCommand"
                             % cmd)

        if cls._allocated_:
            # case allocated
            #   - unable to replace, just append only
            #   - initialize and allocate
            if name in cls._total_dict_:
                raise ValueError(
                    "Please avoid to use '%s' on AppCommand name on class %s,"
                    "or add it before allocation of the class"
                    % (name, cls.__name__))
            cls._commands_.append(name, cmd)
            cmd.initialize(cls)
            cls._total_dict_[name] = cmd

            cmd.allocate(cls.manager)
            cls._cmdtable_.add_pair(name, cmd.get_cmd_ptr())
        else:
            # case not allocated
            #   - replace or add
            #   - just initialize
            if (name in cls._total_dict_
                    and isinstance(cls._total_dict_[name],
                                   appcommand.AppCommandN)):
                raise ValueError("Conflict on attribute - %s.%s"
                                 % (cls.__name__, name))
            if name in cls._commands_:
                cls._commands_.replace(name, cmd)
            else:
                cls._commands_.append(name, cmd)
            cmd.initialize(cls)
            cls._total_dict_[name] = cmd
