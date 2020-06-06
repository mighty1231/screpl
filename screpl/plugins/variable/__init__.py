from eudplib import *

from screpl.apps.repl import REPL
from screpl.core.appcommand import AppCommand
from screpl.main import get_app_manager
from screpl.utils.conststring import EPDConstString
from screpl.utils.referencetable import ReferenceTable

# initialize global variables
manager = get_app_manager()
accessed_resources = set()
death_units = []
watched_eud_vars = ReferenceTable(key_f=EPDConstString)

def explore_triggers():
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

        for condition in conditions:
            condtype = condition[15]
            player = b2i4(condition, 4)
            unitid = b2i2(condition, 12)
            restype = condition[16]

            # search Accumulate
            if condtype == 4 and player <= 26:
                if restype == EncodeResource(Ore):
                    accessed_resources.add(Ore)
                elif restype == EncodeResource(Gas):
                    accessed_resources.add(Gas)
                elif restype == EncodeResource(OreAndGas):
                    accessed_resources.add(Ore)
                    accessed_resources.add(Gas)
                else:
                    raise RuntimeError("Unknown restype on Accumulate, %d" % restype)

            # search Deaths
            if condtype == 15 and     \
                    player <= 26 and  \
                    unitid not in death_units:
                death_units.append(unitid)

        # search SetDeaths
        for action in actions:
            acttype = action[26]
            player = b2i4(action, 16)
            unitid = b2i2(action, 24)

            if acttype == 45 and      \
                    player <= 26 and  \
                    unitid not in death_units:
                death_units.append(unitid)

        offset += 2400

explore_triggers()

def watch_variable(name, var):
    assert IsEUDVariable(var)
    watched_eud_vars.add_pair(name, EPD(var.getValueAddr()))

def plugin_setup():
    # make commands
    from .varapp import VariableApp

    @AppCommand([])
    def start_command(self):
        """Start VariableApp"""
        manager.start_application(VariableApp)

    REPL.add_command('var', start_command)
