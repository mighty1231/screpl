from eudplib import *

from repl import REPL, get_app_manager, AppCommand

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
dim = GetChkTokenized().getsection(b'DIM ')
mapw = app_manager.getMapWidth()
maph = app_manager.getMapHeight()

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
def startCommand(self):
    app_manager.startApplication(LocationManagerApp)

REPL.add_command('location', startCommand)
