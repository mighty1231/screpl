from eudplib import *

from screpl.apps.repl import REPL
from screpl.core.appcommand import AppCommand
from screpl.main import get_app_manager
from screpl.utils.conststring import EPDConstString
from screpl.utils.referencetable import ReferenceTable

# initialize global variables
manager = get_app_manager()
watched_eud_vars = ReferenceTable(key_f=EPDConstString)

def watch_variable(name, var):
    """Add EUDVariable on watch list, with given name"""
    assert IsEUDVariable(var)
    watched_eud_vars.add_pair(name, EPD(var.getValueAddr()))

condition_writer = None

def plugin_get_dependency():
    """Returns list of required plugins"""
    return []

def plugin_setup():
    global condition_writer

    # make commands
    from .condition import VariableConditionManager

    condition_writer = VariableConditionManager()

    # explore conditions
    orig_triggers = GetChkTokenized().getsection(b'TRIG')
    assert len(orig_triggers) % 2400 == 0

    offset = 0
    while offset < len(orig_triggers):
        trig = orig_triggers[offset:offset+2400]

        # parse triggers
        for i in range(16):
            condition = trig[20*i:20*(i+1)]
            condtype = condition[15]
            player = b2i4(condition, 4)
            unitid = b2i2(condition, 12)
            restype = condition[16]

            if condtype == 0:
                break
            condition_writer.add_entry(condition)

        offset += 2400
    condition_writer.make_funcptrs()

    @AppCommand([])
    def start_command(self):
        """Start VariableApp"""
        from .varapp import VariableApp
        manager.start_application(VariableApp)

    REPL.add_command('var', start_command)
