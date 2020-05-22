from repl import REPL, get_app_manager, AppCommand

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
