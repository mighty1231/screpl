''' plugin sample '''

from eudplib import *
from repl import REPL, getAppManager, AppCommand, EUDByteRW, argEncNumber
from .myapp import MyApp

# MY_COMMAND decides how to invoke the command in-game
# chatting 'openMyApp()' would create the app
MY_COMMAND1 = "open"
MY_COMMAND2 = "hello"

@AppCommand([])
def command1(self):
    '''
    At here, 'self' will become REPL instance
    Note that codes after startApplication will not executed
    '''
    getAppManager().startApplication(MyApp)

@AppCommand([argEncNumber])
def command2(self, n):
    '''
    print("hello? " * n)
    '''
    rw = EUDByteRW()
    rw.seekepd(self.cmd_output_epd)
    i = EUDVariable()
    i << 0
    if EUDWhile()(i < n):
        rw.write_f("Hello? ")
        i += 1
    EUDEndWhile()
    rw.write(0)

REPL.addCommand(MY_COMMAND1, command1)
REPL.addCommand(MY_COMMAND2, command2)
