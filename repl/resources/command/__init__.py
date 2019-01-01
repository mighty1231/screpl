from .basics import register_basiccmds
from .conditions import register_all_conditioncmds
from .actions import register_all_actioncmds
from .utils import register_utilcmds

def register_cmds():
	register_basiccmds()
	register_all_conditioncmds()
	register_all_actioncmds()
	register_utilcmds()
