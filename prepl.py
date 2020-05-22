from eudplib import *
import importlib, re
import screpl.main as main

default_settings = {
    'superuser'     : 'P1',
    'superuser_mode': 'playerID',
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

    if settings["superuser_mode"] == "playerID":
        superuser = playerMap.get(settings["superuser"], settings["superuser"])
        main.initialize_with_id(EncodePlayer(superuser))
    elif settings["superuser_mode"] == "playerName":
        main.initialize_with_name(settings["superuser"])
    else:
        raise RuntimeError("Unknown mode {}".format(settings["superuser_mode"]))

    main.set_bridge_mode(settings["bridge_mode"])

    # load plugins
    # split plugins with ',' or ' '
    plugins = re.split(',| ', settings['plugins'])
    for plugin in plugins:
        if plugin:
            importlib.import_module(plugin)

def afterTriggerExec():
    main.run()

playerMap = {
    'P1':P1,
    'P2':P2,
    'P3':P3,
    'P4':P4,
    'P5':P5,
    'P6':P6,
    'P7':P7,
    'P8':P8,
    'Player1':Player1,
    'Player2':Player2,
    'Player3':Player3,
    'Player4':Player4,
    'Player5':Player5,
    'Player6':Player6,
    'Player7':Player7,
    'Player8':Player8,
}
