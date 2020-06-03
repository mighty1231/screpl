from eudplib import *

from screpl.apps.repl import REPL
from screpl.core.appcommand import AppCommand
from screpl.main import get_app_manager

# initialize variables
app_manager = get_app_manager()
STRSection = EUDVariable()
STRSection_end = EUDVariable()

def plugin_setup():
    STRSection << f_dwread_epd(EPD(0x5993D4))
    STRSection_end << STRSection + app_manager.get_strx_section_size()

    # make commands
    from .manager import TriggerManagerApp

    @AppCommand([])
    def start_command(self):
        app_manager.start_application(TriggerManagerApp)

    REPL.add_command('trigger', start_command)
