from screpl.apps.repl import REPL
from screpl.core.appcommand import AppCommand
from screpl.main import get_app_manager

app_manager = get_app_manager()

from .array import REPLArrayTestApp
from .monitor import MonitorTestApp

apps_to_test = [
    ("testarray", REPLArrayTestApp),
    ("testmonitor", MonitorTestApp),
]

for name, app in apps_to_test:
    @AppCommand([])
    def cmd(self):
        app_manager.startApplication(app)
    REPL.add_command(name, cmd)
