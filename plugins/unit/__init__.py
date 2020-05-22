from eudplib import *

from repl import REPL, get_app_manager, AppCommand

# initialize variables
app_manager = get_app_manager()

# make commands
from .manager import UnitManagerApp

@AppCommand([])
def startCommand(self):
    app_manager.startApplication(UnitManagerApp)

REPL.add_command('unit', startCommand)
