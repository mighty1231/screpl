from eudplib import *
from repl import (
    Application,
    AppMethod,
    AppTypedMethod,
    AppCommand,
    getAppManager,
    argEncNumber,
    Logger,
    IOCheck
)
from repl.core.application import ApplicationInstance

manager = getAppManager()

inputs = EUDCreateVariables(2)
outputs = EUDCreateVariables(2)

@IOCheck
@EUDFunc
def getMax(a, b):
    if EUDIf()(a > b):
        EUDReturn([2*a, a])
    if EUDElseIf()(a < b):
        EUDReturn([b, b])
    EUDEndIf()
    return 100, 100

class TestApp(Application):
    fields = [
        'var',
        'locV'
    ]

    def onInit(self):
        self.var = 0
        self.locV = 1

    def onChat(self, offset):
        '''
        Reads command and execute AppCommands given OFFSET as a string pointer
        '''
        # self.var += 1
        # f_dwwrite_epd(self.cmd_output_epd, 0)
        TestApp.getSuper().onChat(offset)

    def onResume(self):
        DoActions([CreateUnit(self.locV, "Terran SCV", 0, P1)])

    def loop(self):
        if EUDIf()(manager.keyPress("ESC")):
            manager.requestDestruct()
            EUDReturn()
        if EUDElseIf()(manager.keyPress("K")):
            self.var += 1
        if EUDElseIf()(manager.keyPress("G")):
            manager.startApplication(Logger)
            EUDReturn()
        EUDEndIf()
        manager.requestUpdate()

    def print(self, writer):
        writer.write_f("var %D\n", self.var)
        writer.write_f("loc %D\n", self.locV)

        v1 = f_dwread_epd(manager.keystates + ord('A'))
        v2 = f_dwread_epd(manager.keystates_sub + ord('A'))
        writer.write_f("%D %D", v1, v2)
        writer.write_f("Input %D %D\n", *inputs)
        writer.write_f("Output %D %D\n", *outputs)
        writer.write(0)

    @IOCheck
    @AppTypedMethod([None, None], [None, None])
    def decorated(self, a, b):
        if EUDIf()(a > b):
            EUDReturn([2*a, a])
        if EUDElseIf()(a < b):
            EUDReturn([b, b])
        EUDEndIf()
        return 100, 100

    @AppCommand([argEncNumber, argEncNumber])
    def free(self, a, b):
        self.decorated(a, b)

    @IOCheck
    @AppCommand([argEncNumber, argEncNumber])
    def cmd(self, a, b):
        DoActions([
            CreateUnit(a, "Terran SCV", 1, P1),
            CreateUnit(b, "Zerg Drone", 1, P1)
        ])

    @IOCheck
    @AppCommand([argEncNumber, argEncNumber])
    def deco(self, a, b):
        getMax(a, b)
