from eudplib import *

from screpl.apps.repl import REPL
from screpl.core.appcommand import AppCommand
from screpl.main import get_app_manager

keymap = {
    "manager" : {
        "open_editor" : "E"
    },

    "editor" : {
        "hold": "H",
        "change_grid_mode": "G",
    }
}
FRAME_PERIOD = 24

# initialize variables
app_manager = get_app_manager()

def plugin_get_dependency():
    """Returns list of required plugins"""
    return []

def plugin_setup():
    DoActions([
        # make enable to create "Scanner Sweep"
        SetMemoryX(0x661558, SetTo, 1 << 17, 1 << 17),

        # unit dimension to make visible on the side of the map
        SetMemory(0x6617C8 + 33 * 8, SetTo, 0x00040004),
        SetMemory(0x6617C8 + 33 * 8 + 4, SetTo, 0x00040004)
    ])

    # make commands
    from .manager import LocationManagerApp

    @AppCommand([])
    def start_command(self):
        """Start LocationManagerApp"""
        app_manager.start_application(LocationManagerApp)

    REPL.add_command('location', start_command)
