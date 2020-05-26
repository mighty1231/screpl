from eudplib import *

from screpl.core.appcommand import AppCommand
from screpl.core.application import Application
from screpl.core.appmethod import AppTypedMethod
from screpl.encoder.const import ArgEncNumber
from screpl.monitor.func import repl_monitor_f
from screpl.monitor.profile import repl_monitor_push
from screpl.monitor.profile import repl_monitor_pop

from . import app_manager

def buildfuncs(io, profile):
    @repl_monitor_f(io=io, profile=profile)
    @EUDFunc
    def test_0_2():
        EUDReturn([1, 2])

    @repl_monitor_f(io=io, profile=profile)
    @EUDFunc
    def test_1_0(a):
        pass

    @repl_monitor_f(io=io, profile=profile)
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

    def on_init(self):
        self.var = 0

    def on_destruct(self):
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

    @repl_monitor_f(io=True, profile=False)
    @AppCommand([ArgEncNumber, ArgEncNumber])
    def multi(self, v1, v2):
        self.var = self._multi(v1, v2)

    @repl_monitor_f(io=True, profile=False)
    @AppTypedMethod([None, None], [None])
    def _multi(self, a, b):
        EUDReturn(a+b)

    @repl_monitor_f(io=True, profile=False)
    @AppCommand([ArgEncNumber])
    def c_i(self, a):
        self.var = a

    @repl_monitor_f(io=True, profile=True)
    @AppCommand([])
    def c_ip(self):
        self.var += 1

    @AppCommand([])
    def monitor(self):
        if repl_monitor_push("monitor", profile=True, log=True):
            if repl_monitor_push("moni_pl", profile=True, log=True):
                pass
            repl_monitor_pop()
            if repl_monitor_push("moni_p", profile=True, log=False):
                pass
            repl_monitor_pop()
            if repl_monitor_push("moni_l", profile=False, log=True):
                pass
            repl_monitor_pop()
            if repl_monitor_push("moni_", profile=False, log=False):
                pass
            repl_monitor_pop()
        repl_monitor_pop()

    @repl_monitor_f(io=False, profile=True)
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
        if EUDIf()(app_manager.key_press("ESC")):
            app_manager.request_destruct()
            EUDReturn()
        EUDEndIf()
        app_manager.request_update()

    def print(self, writer):
        writer.write_f("MonitorTestApp var %D\n", self.var)
        writer.write(0)

