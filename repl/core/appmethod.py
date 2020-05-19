from eudplib import *

from eudplib.core.eudfunc.eudtypedfuncn import EUDTypedFuncN, applyTypes
from eudplib.core.eudstruct.vararray import EUDVArrayData
from eudplib.core.eudfunc.eudfptr import createIndirectCaller

import inspect

class AppMethodN:
    def __init__(self, argtypes, rettypes, method, *, getWriterAsParam, traced):
        # Step 1 from parameters
        self.argtypes = argtypes
        self.rettypes = rettypes

        self.method = method
        self.name = method.__name__

        self.getWriterAsParam = getWriterAsParam

        # Step 2 initialize with class
        self.argn = -1
        self.retn = -1
        self.cls = None
        self.index = -1
        self.parent = None
        self.funcptr_cls = None
        self.funcptr = None

        # Step 3 allocate
        self.funcn = None
        self.funcn_callback = None


        self.traced = traced
        self.status = 'not initialized'

    def __repr__(self):
        if self.status == 'not initialized':
            return '<AppMethod %s, st=NI>' % self.name
        elif self.status == 'initialized':
            return '<AppMethod %s.%s, st=I, idx=%d>' % (self.cls.__name__, self.name, self.index)
        elif self.status == 'allocated':
            return '<AppMethod %s.%s, st=A, idx=%d>' % (self.cls.__name__, self.name, self.index)
        else:
            raise RuntimeError

    def getFuncPtr(self):
        return self.funcptr

    def setFuncnCallback(self, funcn_callback):
        if self.status == "allocated":
            raise RuntimeError("AppMethod already has its body")
        assert self.funcn_callback is None
        self.funcn_callback = funcn_callback

    def initialize(self, cls, index, parent = None):
        # initializing from its Application class
        assert self.status == 'not initialized'

        # Get argument number of fdecl_func
        argspec = inspect.getfullargspec(self.method)
        argn = len(argspec.args)
        assert argspec.varargs is None, \
                'No variadic arguments (*args) allowed for AppMethod'
        assert argspec.varkw is None, \
                'No variadic keyword arguments (**kwargs) allowed for AppMethod'

        if parent:
            # override
            assert index == parent.index, 'class %s name %s' % (cls, self.name)
            if self.argtypes:
                assert self.argtypes == parent.argtypes
            else:
                self.argtypes = parent.argtypes

            if self.rettypes:
                assert self.rettypes == parent.rettypes
            else:
                self.rettypes = parent.rettypes

            if parent.getWriterAsParam:
                self.getWriterAsParam = True

        # initialize or check argtype
        if self.argtypes:
            if self.getWriterAsParam:
                assert len(self.argtypes) == argn - 2
            else:
                assert len(self.argtypes) == argn - 1
        else:
            if self.getWriterAsParam:
                self.argtypes = [None for _ in range(argn - 2)]
            else:
                self.argtypes = [None for _ in range(argn - 1)]

        self.argn = len(self.argtypes)
        self.retn = len(self.rettypes)
        self.cls = cls
        self.index = index
        self.parent = parent
        self.funcptr_cls = EUDTypedFuncPtr(self.argtypes, self.rettypes)
        self.funcptr_val = EUDVArrayData(2)([0, 0])
        self.funcptr = self.funcptr_cls(self.funcptr_val)

        self.status = 'initialized'

    def allocate(self):
        if self.status == 'allocated':
            return
        assert self.status == 'initialized'

        from .appmanager import getAppManager

        if not self.getWriterAsParam:
            # Set first argument as AppInstance
            def call(*args):
                instance = getAppManager().getCurrentAppInstance()
                prev_cls = instance._cls
                instance._cls = self.cls

                args = applyTypes(self.argtypes, args)
                ret = self.method(instance, *args)

                instance._cls = prev_cls
                return ret
        else:
            # Additionally set second argument as printer
            def call(*args):
                instance = getAppManager().getCurrentAppInstance()
                prev_cls = instance._cls
                instance._cls = self.cls
                printer = getAppManager().getWriter()

                args = applyTypes(self.argtypes, args)
                ret = self.method(instance, printer, *args)

                instance._cls = prev_cls
                return ret

        funcn = EUDTypedFuncN(
            self.argn, call, self.method, self.argtypes, self.rettypes,
            traced=self.traced)

        if self.funcn_callback:
            if self.getWriterAsParam:
                raise RuntimeError("print() cannot be decorated")
            funcn = self.funcn_callback(funcn)

        funcn._CreateFuncBody()
        f_idcstart, f_idcend = createIndirectCaller(funcn)

        self.funcn = funcn
        self.funcptr_val._initvars = [f_idcstart, EPD(f_idcend + 4)]

        self.status = 'allocated'

    def apply(self):
        from .appmanager import getAppManager
        manager = getAppManager()
        assert self.status in ['initialized', 'allocated'], self
        return self.funcptr_cls.cast(manager.cur_methods[self.index])

    def applyAbsolute(self):
        return self.funcn

    def __call__(self, instance, *args, **kwargs):
        '''
        Direct call - used for superclass method call
        '''
        from .appmanager import getAppManager
        assert id(instance) == id(getAppManager().getCurrentAppInstance())
        return self.funcn(*args, **kwargs)

''' Decorator to make AppMethodN '''
def AppTypedMethod(argtypes, rettypes = [], *, getWriterAsParam=False, traced=False):
    def ret(method):
        return AppMethodN(argtypes, rettypes, method,
                getWriterAsParam=getWriterAsParam, traced=traced)
    return ret

def AppMethod(method):
    return AppTypedMethod(None, [], traced=False)(method)

def AppMethod_writerParam(method):
    return AppTypedMethod(None, [], getWriterAsParam=True, traced=False)(method)
