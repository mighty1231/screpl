from eudplib import *
from repl import (
    Application,
    ScrollApp,
    AppMethod,
    AppTypedMethod,
    AppCommand,
    getAppManager,
    argEncNumber,
    Logger,
    IOCheck
)
from repl.core.application import ApplicationInstance
from . import appManager

a = EUDVariable()
b = EUDVariable()

from ..variable import watchVariable

watchVariable("a", a)
watchVariable("b", b)

class TestApp2(ScrollApp):
    fields = [
        'var'
    ]

    def onInit(self):
        self.var = 0

    def writeTitle(self, writer):
        writer.write_f("hello")

    def writeLine(self, writer, i):
        writer.write_f("write test %D", i)

    def getLineCount(self):
        return self.var

    def loop(self):
        global a, b
        if EUDIf()(appManager.keyPress('F')):
            a += 1
            b += 2
            self.var += 1
        EUDEndIf()
        if EUDIf()(appManager.keyPress('G')):
            a += 100
            b += 200
            self.var = 0
        EUDEndIf()
        if EUDIf()(appManager.keyPress('Q')):
            self.test(a, b)
        EUDEndIf()
        if EUDIf()(appManager.keyPress("E")):
            appManager.startApplication(Logger)
            EUDReturn()
        EUDEndIf()
        ScrollApp.loop(self)

    @IOCheck
    @AppTypedMethod([None, None], [None, None])
    def test(self, a, b):
        self.var += (a + b)
        return 1, 2

    @IOCheck
    @AppMethod
    def test4(self, a, b):
        self.var += (a + b)
