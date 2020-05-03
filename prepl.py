from repl.core.appmanager import AppManager, getAppManager

import importlib, re

default_settings = {
    'superuser'     : 'P1',
    'superuser_mode': 'playerNumber',
    'plugins'       : '',
    'bridge_mode'   : 'off'
}

def combine_settings():
    for key in settings:
        if key not in default_settings:
            raise RuntimeError("Unknown key '%s' in settings" % key)

    for key in default_settings:
        if key not in settings:
            settings[key] = default_settings[key]

def onPluginStart():
    combine_settings()

    # initialize appmanager
    AppManager.initialize(
        superuser = settings["superuser"],
        superuser_mode = settings["superuser_mode"],
        bridge_mode = settings["bridge_mode"]
    )

    # load plugins
    # split plugins with ',' or ' '
    plugins = re.split(',| ', settings['plugins'])
    for plugin in plugins:
        if plugin:
            importlib.import_module(plugin)

def afterTriggerExec():
    getAppManager().loop()
