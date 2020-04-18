from eudplib import *

import inspect

class _AppMethod:
    def __init__(self, argtypes, rettypes, method, *, isPrint, traced):
        # Get argument number of fdecl_func
        argspec = inspect.getargspec(method)
        ep_assert(
            argspec[1] is None,
            'No variadic arguments (*args) allowed for AppMethod.'
        )
        ep_assert(
            argspec[2] is None,
            'No variadic keyword arguments (*kwargs) allowed for AppMethod.'
        )

        argn = len(argspec[0]) - 1 # except self
        if argtypes is None:
            argtypes = [None for _ in range(argn)]
        else:
            assert argn == len(argtypes)
        retn = len(rettypes)

        if isPrint:
            assert argtypes == [None] and argn == 1
            assert rettypes == []
            argtypes = rettypes = []
            argn = retn = 0
        self.isPrint = isPrint

        self.argtypes = argtypes
        self.rettypes = rettypes
        self.argn = argn
        self.retn = retn

        self.method = method
        self.name = method.__name__

        # Step 2 initialize
        self.cls = None
        self.index = -1
        self.parent = None
        self.funcptr_cls = None
        self.funcptr = None

        # Step 3 allocate
        self.funcn = None


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

    def initialize(self, cls, index, parent = None):
        # initializing from its Application class
        assert self.status == 'not initialized'

        # overriding
        if parent:
            assert index == parent.index, 'class %s name %s' % (cls, self.name)
            if parent.isPrint:
                assert self.argtypes == [None] and self.argn == 1
                assert self.rettypes == []
                self.argtypes = self.rettypes = []
                self.argn = self.retn = 0

                self.isPrint = True
            else:
                if self.argtypes is not None:
                    assert self.argtypes == parent.argtypes
                    assert self.argn == parent.argn
                else:
                    self.argtypes = parent.argtypes
                    self.argn = parent.argn

                if self.rettypes is not None:
                    assert self.rettypes == parent.rettypes
                    assert self.retn == parent.retn
                else:
                    self.rettypes = parent.rettypes
                    self.retn = parent.retn

        self.cls = cls
        self.index = index
        self.parent = parent
        self.funcptr_cls = EUDTypedFuncPtr(self.argtypes, self.rettypes)
        self.funcptr = self.funcptr_cls()

        self.status = 'initialized'

    def allocate(self):
        if self.status == 'allocated':
            return
        assert self.status == 'initialized'

        from . import getAppManager
        from eudplib.core.eudfunc.eudtypedfuncn import EUDTypedFuncN, applyTypes

        if not self.isPrint:
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
            def call():
                instance = getAppManager().getCurrentAppInstance()
                prev_cls = instance._cls
                instance._cls = self.cls
                printer = getAppManager().getWriter()

                ret = self.method(instance, printer)
                printer.write(0)

                instance._cls = prev_cls
                return ret

        funcn = EUDTypedFuncN(
            self.argn, call, self.method, self.argtypes, self.rettypes,
            traced=self.traced)

        funcn._CreateFuncBody()

        self.funcn = funcn
        self.funcptr << self.funcn

        self.status = 'allocated'

    def apply(self):
        from . import getAppManager
        manager = getAppManager()
        assert self.status in ['initialized', 'allocated'], self
        return self.funcptr_cls.cast(manager.cur_methods[self.index])

    def applyAbsolute(self):
        return self.funcn

''' Decorator to make _AppMethod '''
def AppTypedMethod(argtypes, rettypes = [], *, isPrint=False, traced=False):
    def ret(method):
        return _AppMethod(argtypes, rettypes, method, isPrint=isPrint, traced=traced)
    return ret

def AppMethod(method):
    return AppTypedMethod(None, [], traced=False)(method)

# special method
def AppMethod_print(method):
    return AppTypedMethod(None, [], isPrint=True, traced=False)(method)
