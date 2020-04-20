from eudplib import *

from repl import REPL, getAppManager, AppCommand, argEncNumber
from .app import MemoryApp

manager = getAppManager()

@AppCommand([argEncNumber, argEncNumber])
def openWithPtr(self, ptr, size):
    MemoryApp.setContent_ptr(ptr, size)
    manager.openApplication(MemoryApp)

@AppCommand([argEncNumber, argEncNumber])
def openWithEpd(self, epd, size):
    MemoryApp.setContent_epd(epd, size)
    manager.openApplication(MemoryApp)

REPL.addCommand('memptr', openWithPtr)
REPL.addCommand('memepd', openWithEpd)
