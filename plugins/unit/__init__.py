from eudplib import *

from screpl.apps.repl import REPL
from screpl.core.appcommand import AppCommand
from screpl.main import get_app_manager

# initialize variables
app_manager = get_app_manager()

# make commands
from .manager import UnitManagerApp

@AppCommand([])
def startCommand(self):
    app_manager.startApplication(UnitManagerApp)

REPL.add_command('unit', startCommand)
