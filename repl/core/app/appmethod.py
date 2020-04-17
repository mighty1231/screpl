from eudplib import *

import inspect

class _AppMethod:
    def __init__(self, argtypes, rettypes, method, *, isPrint, traced):
        # Get argument number of fdecl_func
        argspec = inspect.getargspec(method)
        argn = len(argspec[0]) - 1 # except self
        ep_assert(
            argspec[1] is None,
            'No variadic arguments (*args) allowed for AppMethod.'
        )
        ep_assert(
            argspec[2] is None,
            'No variadic keyword arguments (*kwargs) allowed for AppMethod.'
        )

        if argtypes is None:
            argtypes = [None for _ in range(argn)]

        assert argn == len(argtypes)
        self.argtypes = argtypes

        self.rettypes = rettypes
        self.argn = argn
        self.retn = None

        self.method = method
        self.funcptr = None
        self.index = -1

        self.parent = None

        self.isPrint = isPrint
        self.traced = traced

        if isPrint:
            assert self.argtypes == [None] and self.argn == 1
            assert self.rettypes == None
            self.argtypes = self.rettypes = []
            self.argn = 0

    def getFuncPtr(self):
        assert self.funcptr is not None
        return self.funcptr

    def setParent(self, parent):
        # Overriding method, some members are replicated
        assert self.index == parent.index == -1, "Should not be initialized"
        if parent.isPrint:
            self.isPrint = True

            assert self.argtypes == [None] and self.argn == 1
            assert self.rettypes == None
            self.argtypes = self.rettypes = []
            self.argn = 0
        else:
            if self.argtypes is not None:
                assert self.argtypes == parent.argtypes
                assert self.argn == parent.argn
            else:
                self.argtypes = parent.argtypes
                self.argn = parent.argn
        self.parent = parent

    def initialize(self, cls, index):
        from . import getAppManager
        from eudplib.core.eudfunc.eudtypedfuncn import EUDTypedFuncN, applyTypes

        if self.index != -1:
            assert self.index == index
            return

        if not self.isPrint:
            # Set first argument as AppInstance
            def call(*args):
                instance = getAppManager().getCurrentAppInstance()
                prev_cls = instance._cls
                instance._cls = cls

                args = applyTypes(self.argtypes, args)
                ret = self.method(instance, *args)

                instance._cls = prev_cls
                return ret

            funcn = EUDTypedFuncN(
                self.argn, call, self.method, self.argtypes, self.rettypes,
                traced=self.traced)

            funcn._CreateFuncBody()
            if self.rettypes is None:
                self.rettypes = [None for _ in range(funcn._retn)]
        else:
            # Additionally set second argument as printer
            def call():
                instance = getAppManager().getCurrentAppInstance()
                prev_cls = instance._cls
                instance._cls = cls
                printer = getAppManager().getWriter()

                ret = self.method(instance, printer)

                instance._cls = prev_cls
                return ret
            funcn = EUDTypedFuncN(
                0, call, self.method, self.argtypes, self.rettypes,
                traced=self.traced)

            funcn._CreateFuncBody()
            assert funcn._retn == 0

        self.funcn = funcn
        self.index = index

        self.funcptr_cls = EUDTypedFuncPtr(self.argtypes, self.rettypes)
        self.funcptr = self.funcptr_cls(_from = funcn)
        self.funcptr << self.funcn

        # overriding check - returning arguments
        if self.parent:
            assert self.index == self.parent.index, 'class %s name %s' % (cls, self.method.__name__)
            assert self.rettypes == self.parent.rettypes, 'class %s name %s' % (cls, self.method.__name__)
            assert self.retn == self.parent.retn, 'class %s name %s' % (cls, self.method.__name__)

    def apply(self, instance):
        from . import ApplicationInstance
        assert self.index != -1
        assert isinstance(instance, ApplicationInstance)
        return self.funcptr_cls.cast(instance._mvarr[self.index])

''' Decorator to make _AppMethod '''
def AppTypedMethod(argtypes, rettypes = None, *, isPrint=False, traced=False):
    def ret(method):
        return _AppMethod(argtypes, rettypes, method, isPrint=isPrint, traced=traced)
    return ret

def AppMethod(method):
    return AppTypedMethod(None, None, traced=False)(method)

# special method
def AppMethod_print(method):
    return AppTypedMethod(None, None, isPrint=True, traced=False)(method)
