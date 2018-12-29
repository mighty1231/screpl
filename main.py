from eudplib import *

@EUDFunc
def main():
	from repl import onPluginStart, beforeTriggerExec

	onPluginStart()
	if EUDInfLoop()():
		beforeTriggerExec()
		RunTrigTrigger()
		EUDDoEvents()
	EUDEndInfLoop()

from config import outfname
LoadMap("base.scx")
SaveMap(outfname, main)
