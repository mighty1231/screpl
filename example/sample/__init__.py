"""plugin sample"""

from eudplib import *

from screpl.apps.repl import REPL
from screpl.main import get_app_manager
from screpl.core.appcommand import AppCommand
from screpl.utils.byterw import REPLByteRW
from screpl.encoder.const import ArgEncNumber
from .myapp import MyApp

# MY_COMMAND decides how to invoke the command in-game
# chatting 'open()' would create the app
MY_COMMAND1 = "open"
MY_COMMAND2 = "hello"

@AppCommand([])
def command1(self):
    """AppCommand that may be connected to REPL

    At here, 'self' will become REPL instance
    Note that codes after start_application will not executed
    """
    get_app_manager().start_application(MyApp)

@AppCommand([ArgEncNumber])
def command2(self, n):
    """AppCommand that may be connected to REPL

    It is same to following python code:

    .. code-block: python

        print("hello " * n)
    """
    rw = REPL.get_output_writer()
    i = EUDVariable()
    i << 0
    if EUDWhile()(i < n):
        rw.write_f("hello ")
        i += 1
    EUDEndWhile()
    rw.write(0)

REPL.add_command(MY_COMMAND1, command1) # open() may start MyApp
REPL.add_command(MY_COMMAND2, command2) # hello(5) may print 5 "hello"s
