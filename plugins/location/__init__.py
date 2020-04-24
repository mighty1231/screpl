from eudplib import *
from eudplib.core.mapdata.stringmap import locmap

from repl import REPL, getAppManager, AppCommand, EUDByteRW, EPDConstString

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
appManager = getAppManager()
arr = [0 for _ in range(256)]
for string, locid in locmap._s2id.items():
    arr[locid + 1] = EPDConstString(string)
locstrings = EUDArray(arr)

dim = GetChkTokenized().getsection(b'DIM ')
mapw = b2i2(dim, 0)
maph = b2i2(dim, 2)


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
    appManager.startApplication(LocationManagerApp)

REPL.addCommand('location', startCommand)
