"""Application sample for SC-REPL

A series of methods is executed in each frame as follows.

Case 1. app starts with app_manager.startApplication(app)
  - on_init, (on_chat), loop, print

Case 2. If 'on_chat' or 'loop' invoked 'app_manager.request_update()',
  - (on_chat), loop, print

Case 3. If 'on_chat' or 'loop' did not invoked 'app_manager.request_update()',
  - (on_chat), loop

Case 4. If 'on_chat' or 'loop' invoked 'app_manager.request_destruct()'
  - (on_chat), loop, on_destruct

Case 5. Previously launched app is dead,
  - on_resume, (on_chat), loop
"""

from eudplib import *
from screpl.core.appcommand import AppCommand
from screpl.core.application import Application
from screpl.core.appmethod import AppTypedMethod
from screpl.encoder.const import ArgEncNumber
from screpl.main import get_app_manager

manager = get_app_manager()

class MyApp(Application):
    fields = [
        'var1',
        'var2',
        'trial'
    ]

    def on_init(self):
        """Initialize members

        Caution. Avoid to use lshift (ex. self.var1 << 0)
        """
        self.var1 = 0
        self.var2 = 341
        self.trial = 0

    def on_destruct(self):
        """You may free variable that had allocated on init()"""

    def on_chat(self, address):
        """Callback for super user chat

        As default behavior, (from Application class), it reads command
        and execute AppCommands given  OFFSET as a string pointer as a
        default.
        """
        self.trial += 1
        Application.on_chat(self, address)

    def on_resume(self):
        """Called exactly once after newly started app was dead"""
        pass

    def loop(self):
        """Called for every loop during the app is on foreground

        You may make the way to destruct your app. This example destruct
        itself with pressing ESC, but it does not have to.
        """
        if EUDIf()(manager.key_press("ESC")):
            manager.request_destruct()
        EUDEndIf()

        self.var1 += 1
        self.no_return(self.var1)
        manager.request_update()

    def print(self, writer):
        """Called for every request for text UI.

        It may print text ui using REPLByteRW
        """
        writer.write_f('var1 = %D\n', self.var1)
        writer.write_f('var2 = %D\n', self.var2)

    def no_return(self, a):
        """Methods with no returns"""
        self.var2 = a // 4

    @AppTypedMethod([None, None], [None, None])
    def some_returns(self, a, b):
        """Methods with some returns

        Those methods have to be decorated with AppTypedMethod
        """
        plus = a + b
        multiply = a * b
        DoActions([
            CreateUnit(plus, "Terran Firebat", 1, P1),
            CreateUnit(multiply, "Terran Marine", 1, P1),
        ])
        EUDReturn(plus, multiply)

    @AppCommand([ArgEncNumber, ArgEncNumber])
    def plus(self, x, y):
        """AppCommand example

        In-game chat like "plus(3, 4)" will call this with x=3, y=4.
        """
        DoActions([
            CreateUnit(x, "Zerg Zergling", 1, P1),
            CreateUnit(y, "Zerg Hydralisk", 1, P1),
        ])
        c, d = self.some_returns(x, y)
        self.var1 = c
        self.var2 = d
