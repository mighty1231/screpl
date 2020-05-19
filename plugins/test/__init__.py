from repl import REPL, getAppManager, AppCommand

appManager = getAppManager()

from .array import ArrayTestApp
from .monitor import MonitorTestApp

apps_to_test = [
    ("testarray", ArrayTestApp),
    ("testmonitor", MonitorTestApp),
]

for name, app in apps_to_test:
    @AppCommand([])
    def cmd(self):
        appManager.startApplication(app)
    REPL.addCommand(name, cmd)
