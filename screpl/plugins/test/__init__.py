from screpl.apps.repl import REPL
from screpl.core.appcommand import AppCommand
from screpl.main import get_app_manager

app_manager = get_app_manager()

def make_command(app):
    """Make command avoiding late binding problem

    https://stackoverflow.com/a/3431699
    """
    @AppCommand([])
    def cmd(self):
        app_manager.start_application(app)
    cmd.func.__doc__ = "Command to test %s" % app.__name__
    return cmd

def plugin_setup():
    from .array import REPLArrayTestApp
    from .monitor import MonitorTestApp

    apps_to_test = [
        ("testarray", REPLArrayTestApp),
        ("testmonitor", MonitorTestApp),
    ]

    for name, app in apps_to_test:
        REPL.add_command(name, make_command(app))
