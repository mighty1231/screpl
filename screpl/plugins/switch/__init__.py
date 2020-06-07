"""switch (trigger-Switch, SetSwitch) plugin"""
from eudplib import *

from screpl.apps.repl import REPL
from screpl.core.appcommand import AppCommand
from screpl.main import get_app_manager

# initialize variables
app_manager = get_app_manager()

def plugin_setup():
    # make commands
    from .manager import SwitchManagerApp

    @AppCommand([])
    def start_command(self):
        """Start SwitchManagerApp"""
        app_manager.start_application(SwitchManagerApp)

    REPL.add_command('switch', start_command)
