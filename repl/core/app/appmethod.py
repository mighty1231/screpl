from eudplib import *

import inspect, functools
from .appmanager import getAppManager
from .application import ApplicationInstance, Application

@cachedfunc
def getMethodPtr(argtypes, rettypes):
    return EUDTypedFuncPtr(argtypes, rettypes)

class _AppMethod:
    def __init__(self, argtypes, rettypes, method):
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

        self.argtypes = argtypes
        self.rettypes = rettypes
        self.argn = len(argtypes)
        self.retn = len(rettypes)

        self.method = method

        self.funcptr = EUDTypedFuncPtr(argtypes, rettypes)()
        self.index = -1

    def getFuncPtr(self):
        assert self.funcptr is not None
        return self.funcptr

    def initialize(self, cls, index):
        if self.funcptr is not None:
            return

        def call_inner(*args):
            instance = getApplicationManager().getCurrentAppInstance()
            prev_cls = instance._cls
            instance._cls = cls

            args = applyTypes(argtypes, args)
            ret = self.method(instance, *args)

            instance._cls = prev_cls
            return ret

        self.funcn = EUDTypedFuncN(
            self.argn, call_inner, self.method, self.argtypes, self.rettypes,
            traced=traced)
        self.index = index
        self.funcptr << self.funcn

    def apply(self, instance):
        assert self.index != -1
        assert isinstance(instance, ApplicationInstance)
        return EUDTypedFuncPtr(argtypes, rettypes).cast(instance._mvarr[self.index])

''' Decorator to make _AppMethod '''
def AppTypedMethod(argtypes, rettypes = None, *, traced=False):
    def ret(method):
        return _AppMethod(argtypes, rettypes, method)
    return ret

def AppMethod(method):
    # return AppTypedMethod(None, None, traced=False)(method)
    raise NotImplemented
