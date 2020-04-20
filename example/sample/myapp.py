'''
Application sample for REPL

A series of methods is executed in each frame as follows.

Case 1. app starts with getAppManager().startApplication(app)
  - init, (onChat), loop, print

Case 2. If 'onChat' or 'loop' invoked 'getAppManager().requestUpdate()',
  - (onChat), loop, print

Case 3. If 'onChat' or 'loop' did not invoked 'getAppManager().requestUpdate()',
  - (onChat), loop

Case 4. If 'onChat' or 'loop' invoked 'getAppManager().requestDestruct()'
  - (onChat), loop, destruct

Case 5. Previously launched app is dead,
  - onResume, (onChat), loop
  - 
'''

from eudplib import *
from repl import (
    Application,
    AppTypedMethod,
    AppCommand,
    getAppManager,
    argEncNumber
)

manager = getAppManager()

class MyApp(Application):
    fields = [
        'var1',
        'var2',
        'trial'
    ]

    def init(self):
        '''
        Initialize members

        'cmd_output_epd' is reserved member to get results of onChats (compile error etc.)
        If those results are not necessary, set self.cmd_output_epd as 0

        Caution. Avoid to use lshift (ex. self.var1 << 0)
        '''
        self.cmd_output_epd = manager.allocDb_epd(16 // 4)
        self.var1 = 0
        self.var2 = 341
        self.trial = 0

    def destruct(self):
        '''
        You should free variable that had allocated on init()
        '''
        manager.freeDb_epd(self.cmd_output_epd)

    def onChat(self, offset):
        '''
        It reads command and execute AppCommands given OFFSET as a string pointer as a default
        '''
        self.trial += 1
        f_dwwrite_epd(self.cmd_output_epd, 0)
        MyApp.getSuper().onChat(offset)

    def onResume(self):
        '''
        It is executed exactly once when previously launched app was dead
        '''
        pass

    def loop(self):
        '''
        You may make the way to destruct your app.
        This example destruct itself with pressing ESC,
          but it does not necessarily to be pressing ESC
        '''
        if EUDIf()(manager.keyPress("ESC")):
            manager.requestDestruct()
            EUDReturn()
        EUDEndIf()

        self.var1 += 1
        self.noReturn(self.var1)
        manager.requestUpdate()

    def print(self, writer):
        '''
        writer.write_f()
        '''
        writer.write_f('var1 = %D\n', self.var1)
        writer.write_f('var2 = %D\n', self.var2)
        writer.write_f('cmd result -> %D: %E\n', self.trial, self.cmd_output_epd)

    def noReturn(self, a):
        self.var2 = a // 4

    @AppTypedMethod([None, None], [None, None])
    def someReturns(self, a, b):
        '''
        Some methods that should have return must be decorated with AppTypedMethod
          - AppTypedMethod(argtypes, rettypes)
        '''
        plus = a + b
        multiply = a * b
        DoActions([
            CreateUnit(plus, "Terran Firebat", 1, P1),
            CreateUnit(multiply, "Terran Marine", 1, P1),
        ])
        EUDReturn(plus, multiply)

    @AppCommand([argEncNumber, argEncNumber])
    def plus(self, x, y):
        '''
        In-game chat like "plus(3, 4)" executes this part
        '''
        DoActions([
            CreateUnit(x, "Zerg Zergling", 1, P1),
            CreateUnit(y, "Zerg Hydralisk", 1, P1),
        ])
        c, d = self.someReturns(x, y)
        self.var1 = c
        self.var2 = d
