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

from . import appManager
appManager = getAppManager()

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

a = Db(2000)
printval = EUDVariable()

class TestApp(Application):
    fields = [
        'var',
        'locV'
    ]

    def onInit(self):
        self.var = 0
        self.locV = 1
        STRSection, STRSection_epd = f_dwepdread_epd(EPD(0x5993D4))
        _offset_1 = STRSection_epd + 1
        Logger.format("%H %H", STRSection, STRSection_epd)
        for i in [0, 1, 2, 3, 2, 1]:
            Logger.format(str(i) + " %D %D",
                EUDVariable(RlocInt_C(i, 4)) - STRSection,
                EUDVariable(RlocInt_C(i, 1)) - STRSection_epd)

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
        global a
        vv = EUDVariable(a)
        Logger.format("%H %H %H", vv, EPD(vv), EUDVariable(EPD(a)))
        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
            EUDReturn()
        if EUDElseIf()(appManager.keyPress("K")):
            self.var += 1
        if EUDElseIf()(appManager.keyPress("G")):
            appManager.startApplication(Logger)
            EUDReturn()
        EUDEndIf()
        appManager.requestUpdate()

        a, b = Forward(), Forward()
        a << RawTrigger(
            actions = [SetNextPtr(a, b)]
            )
        Logger.format("ab")

        b  << NextTrigger()
        Logger.format("bbb")


    def print(self, writer):
        writer.write_f("var %D\n", self.var)
        writer.write_f("loc %D\n", self.locV)

        v1 = f_dwread_epd(appManager.keystates + ord('A'))
        v2 = f_dwread_epd(appManager.keystates_sub + ord('A'))
        writer.write_f("%D %D", v1, v2)
        writer.write_f("Input %D %D\n", *inputs)
        writer.write_f("Output %D %D\n", *outputs)
        writer.write_f("%I8d %I8u\n", printval, printval)
        writer.write_f("%I16d %I16u\n", printval, printval)
        writer.write_f("%I32d %I32u\n", printval, printval)
        writer.write(0)

    @AppCommand([argEncNumber])
    def pp(self, number):
        printval << number

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
