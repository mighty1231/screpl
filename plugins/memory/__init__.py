from repl import REPL, get_app_manager, AppCommand, argEncNumber
from .memoryapp import MemoryApp

manager = get_app_manager()

@AppCommand([argEncNumber, argEncNumber])
def startWithPtr(self, ptr, size):
    MemoryApp.setContent_ptr(ptr, size)
    manager.startApplication(MemoryApp)

@AppCommand([argEncNumber, argEncNumber])
def startWithEpd(self, epd, size):
    MemoryApp.setContent_epd(epd, size)
    manager.startApplication(MemoryApp)

REPL.addCommand('memptr', startWithPtr)
REPL.addCommand('memepd', startWithEpd)
