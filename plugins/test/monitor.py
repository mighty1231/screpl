from eudplib import *
from repl import (
    Application,
    AppCommand,
    AppTypedMethod,
    argEncNumber,
    REPLMonitorPush,
    REPLMonitorPop,
    REPLMonitorF
)

from . import app_manager

def buildfuncs(io, profile):
    @REPLMonitorF(io=io, profile=profile)
    @EUDFunc
    def test_0_2():
        EUDReturn([1, 2])

    @REPLMonitorF(io=io, profile=profile)
    @EUDFunc
    def test_1_0(a):
        pass

    @REPLMonitorF(io=io, profile=profile)
    @EUDFunc
    def test_2_1(a, b):
        EUDReturn(a + b)

    return [test_0_2, test_1_0, test_2_1]

funcs_ioprofile = buildfuncs(True, True)
funcs_io = buildfuncs(True, False)
funcs_profile = buildfuncs(False, True)
funcs_ = buildfuncs(False, False)

class MonitorTestApp(Application):
    fields = ['var']

    def onInit(self):
        self.var = 0

    def onDestruct(self):
        pass

    @AppCommand([])
    def f_ip(self):
        t02, t10, t21 = funcs_ioprofile
        t02()
        t10(3)
        t21(4, 5)

    @AppCommand([])
    def f_i(self):
        t02, t10, t21 = funcs_io
        t02()
        t10(3)
        t21(4, 5)

    @AppCommand([])
    def f_p(self):
        t02, t10, t21 = funcs_profile
        t02()
        t10(3)
        t21(4, 5)

    @AppCommand([])
    def f_(self):
        t02, t10, t21 = funcs_
        t02()
        t10(3)
        t21(4, 5)

    @REPLMonitorF(io=True, profile=False)
    @AppCommand([argEncNumber, argEncNumber])
    def multi(self, v1, v2):
        self.var = self._multi(v1, v2)

    @REPLMonitorF(io=True, profile=False)
    @AppTypedMethod([None, None], [None])
    def _multi(self, a, b):
        EUDReturn(a+b)

    @REPLMonitorF(io=True, profile=False)
    @AppCommand([argEncNumber])
    def c_i(self, a):
        self.var = a

    @REPLMonitorF(io=True, profile=True)
    @AppCommand([])
    def c_ip(self):
        self.var += 1

    @AppCommand([])
    def monitor(self):
        if REPLMonitorPush("monitor", profile=True, log=True):
            if REPLMonitorPush("moni_pl", profile=True, log=True):
                pass
            REPLMonitorPop()
            if REPLMonitorPush("moni_p", profile=True, log=False):
                pass
            REPLMonitorPop()
            if REPLMonitorPush("moni_l", profile=False, log=True):
                pass
            REPLMonitorPop()
            if REPLMonitorPush("moni_", profile=False, log=False):
                pass
            REPLMonitorPop()
        REPLMonitorPop()

    @REPLMonitorF(io=False, profile=True)
    @AppCommand([])
    def heavy(self):
        i = EUDVariable()
        i << 0
        if EUDInfLoop()():
            EUDBreakIf(i >= 10000)
            f_div(f_dwread_epd(EPD(0x59CCAC)), i)
            i += 1
        EUDEndInfLoop()

    def loop(self):
        if EUDIf()(app_manager.keyPress("ESC")):
            app_manager.requestDestruct()
            EUDReturn()
        EUDEndIf()
        app_manager.requestUpdate()

    def print(self, writer):
        writer.write_f("MonitorTestApp var %D\n", self.var)
        writer.write(0)

