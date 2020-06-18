from eudplib import *

from screpl.apps.repl import REPL
from screpl.core.appcommand import AppCommand
from screpl.main import get_app_manager

FRAME_PERIOD = 24

# initialize variables
app_manager = get_app_manager()

def plugin_get_dependency():
    """Returns list of required plugins"""
    return []

def plugin_setup():
    # make commands
    from .manager import LocationManagerApp

    @AppCommand([])
    def start_command(self):
        """Start LocationManagerApp"""
        app_manager.start_application(LocationManagerApp)

    REPL.add_command('location', start_command)
