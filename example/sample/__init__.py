''' plugin sample '''

from eudplib import *
from screpl import REPL, get_app_manager, AppCommand, REPLByteRW, ArgEncNumber
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
    get_app_manager().startApplication(MyApp)

@AppCommand([ArgEncNumber])
def command2(self, n):
    '''
    print("hello? " * n)
    '''
    rw = REPLByteRW()
    rw.seekepd(self.cmd_output_epd)
    i = EUDVariable()
    i << 0
    if EUDWhile()(i < n):
        rw.write_f("Hello? ")
        i += 1
    EUDEndWhile()
    rw.write(0)

REPL.add_command(MY_COMMAND1, command1)
REPL.add_command(MY_COMMAND2, command2)
