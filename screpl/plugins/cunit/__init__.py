from eudplib import *

from screpl.apps.repl import REPL
from screpl.core.appcommand import AppCommand
from screpl.main import get_app_manager
from screpl.utils.array import REPLArray

# initialize variables
app_manager = get_app_manager()

# members
from .cunitrw import cu_members
cu_mem_activeids = REPLArray.construct(cu_members.length, list(range(cu_members.length)))
cu_mem_activeid_contents = EUDVariable()

def plugin_setup():
    global cu_mem_activeids, cu_mem_activeid_contents

    cu_mem_activeid_contents << cu_mem_activeids.contents
    # make commands
    from .manager import CUnitManagerApp

    @AppCommand([])
    def start_command(self):
        """Start CUnitManagerApp"""
        app_manager.start_application(CUnitManagerApp)

    REPL.add_command('cunit', start_command)
