from screpl.apps.repl import REPL
from screpl.core.appcommand import AppCommand
from screpl.encoder.const import ArgEncNumber
from screpl.main import get_app_manager

from .memoryapp import MemoryApp

def plugin_setup():
    manager = get_app_manager()

    @AppCommand([ArgEncNumber, ArgEncNumber])
    def start_with_ptr(self, ptr, size):
        """Start memory viewer on ptr, with given size"""
        MemoryApp.set_content_ptr(ptr, size)
        manager.start_application(MemoryApp)

    @AppCommand([ArgEncNumber, ArgEncNumber])
    def start_with_epd(self, epd, size):
        """Start memory viewer on epd, with given size"""
        MemoryApp.set_content_epd(epd, size)
        manager.start_application(MemoryApp)

    REPL.add_command('memptr', start_with_ptr)
    REPL.add_command('memepd', start_with_epd)
