from eudplib import *

from repl import REPL, getAppManager, AppCommand, EPDConstString, ReferenceTable

# initialize global variables
manager = getAppManager()
death_units = []
watched_eud_vars = ReferenceTable(key_f=EPDConstString)

def getUsedDeathUnits():
    orig_triggers = GetChkTokenized().getsection(b'TRIG')
    assert len(orig_triggers) % 2400 == 0

    offset = 0
    while offset < len(orig_triggers):
        trig = orig_triggers[offset:offset+2400]

        # parse triggers
        conditions = []
        for i in range(16):
            condition = trig[20*i:20*(i+1)]
            conditions.append(condition)

        # parse actions
        actions = []
        for i in range(64):
            action = trig[16*20+32*i:16*20+32*(i+1)]
            actions.append(action)

        # find Deaths and SetDeaths
        for condition in conditions:
            condtype = condition[15]
            player = b2i4(condition, 4)
            unitid = b2i2(condition, 12)

            if condtype == 15 and     \
                    player <= 26 and  \
                    unitid not in death_units:
                death_units.append(unitid)

        for action in actions:
            acttype = action[26]
            player = b2i4(action, 16)
            unitid = b2i2(action, 24)

            if acttype == 45 and      \
                    player <= 26 and  \
                    unitid not in death_units:
                death_units.append(unitid)

        offset += 2400

getUsedDeathUnits()

def watchVariable(name, var):
    assert IsEUDVariable(var)
    watched_eud_vars.AddPair(name, EPD(var.getValueAddr()))

# make commands
from .varapp import VariableApp

@AppCommand([])
def startCommand(self):
    manager.startApplication(VariableApp)

REPL.addCommand('var', startCommand)
