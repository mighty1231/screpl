"""Plugin manager for SC-REPL

SC-REPL plugins support SC-REPL with various apps. They may define special
functions to explain themselves to SC-REPL:

.. function:: plugin_get_dependency()

    Returns list of plugins with string

.. function:: plugin_setup()

    Some triggers may called on this function. It is exactly called once.

Example plugin. Its directory structure:

.. code-block:: bash

    my_plugin
    ├── __init__.py
    └── app.py # defines MyApp

The contents on __init__.py may be::

    from screpl.apps.repl import REPL
    from screpl.core.appcommand import AppCommand
    from screpl.main import get_app_manager
    from screpl.plugins.cunit.detail import CUnitDetailApp
    from .app import MyApp

    @AppCommand
    def cmd1(self):
        get_app_manager().start_application(MyApp)

    @AppCommand
    def cmd2(self):
        CUnitDetailApp.setFocus_epd(EPD(0x59CCA8))
        get_app_manager().start_application(CUnitDetailApp)

    def plugin_get_dependency():
        return ["screpl.plugins.cunit"]

    def plugin_setup():
        DoActions(DisplayText("My plugin is going to be setup!"))

        REPL.add_command("cmd1", cmd1)
        REPL.add_command("cmd2", cmd2)

"""
from eudplib import NextTrigger
from importlib import import_module

class PluginError(Exception):
    """Plugin error on load"""

class PluginManager:
    def __init__(self, plugins=None):
        """Load plugins as default

        Args:
            plugins (list): list of plugins given with module, default to None

        Example::

            PluginManager(["screpl.plugins.unit",
                           "screpl.plugins.location"])
        """
        self.plugins = []

        if plugins:
            for plugin in plugins:
                self.load_plugin(plugin)

    def load_plugin(self, plname):
        """Load screpl plugin"""
        if plname == '':
            return

        trig = NextTrigger()
        mod = import_module(plname)
        if trig.IsSet():
            raise PluginError("Plugin %s has a trigger on outside the "
                              "function plugin_setup(), which is not allowed"
                              % plname)

        # duplication check
        if id(mod) in self.plugins:
            return
        self.plugins.append(id(mod))

        plugin_get_dependency = getattr(mod,
                                        'plugin_get_dependency',
                                        None)

        if not plugin_get_dependency:
            raise PluginError(
                "Plugin %s has no plugin_get_dependency() function; "
                "is it really a SC-REPL plugin module?"
                % plname)

        for dep_plname in plugin_get_dependency():
            self.load_plugin(dep_plname)

        plugin_setup = getattr(mod, 'plugin_setup', None)
        if not plugin_setup:
            raise PluginError(
                "Plugin %s has no plugin_setup() function; "
                "is it really a SC-REPL plugin module?"
                % plname)

        plugin_setup()
