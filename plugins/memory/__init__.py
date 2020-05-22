from screpl.apps.repl import REPL
from screpl.core.appcommand import AppCommand
from screpl.encoder.const import ArgEncNumber
from screpl.main import get_app_manager

from .memoryapp import MemoryApp

manager = get_app_manager()

@AppCommand([ArgEncNumber, ArgEncNumber])
def startWithPtr(self, ptr, size):
    MemoryApp.setContent_ptr(ptr, size)
    manager.startApplication(MemoryApp)

@AppCommand([ArgEncNumber, ArgEncNumber])
def startWithEpd(self, epd, size):
    MemoryApp.setContent_epd(epd, size)
    manager.startApplication(MemoryApp)

REPL.add_command('memptr', startWithPtr)
REPL.add_command('memepd', startWithEpd)
