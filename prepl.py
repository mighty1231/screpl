from eudplib import *
from repl import REPL, getAppManager, AppCommand

import importlib, re

manager = None

def onPluginStart():
    global manager

    # set superuser
    pid = 0 # default as P1
    if 'superuser' in settings:
        su = playerMap.get(settings['superuser'], settings['superuser'])
        pid = EncodePlayer(su)
    if pid not in range(7):
        raise RuntimeError('Superuser in REPL should be one of P1~P8')

    # make AppManager instance with superuser
    manager = getAppManager(superuser = pid)

    # load plugins
    # split plugins with ',' or ' '
    if 'plugins' in settings:
        plugins = re.split(',| ', settings['plugins'])
        for plugin in plugins:
            if plugin:
                importlib.import_module(plugin)

def beforeTriggerExec():
    manager.loop()

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
