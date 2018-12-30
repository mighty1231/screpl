from eudplib import *

@EUDFunc
def main():
	from repl import beforeTriggerExec

	if EUDInfLoop()():
		# Turbo
		DoActions(SetDeaths(203151, SetTo, 1, 0))

		beforeTriggerExec()
		RunTrigTrigger()
		EUDDoEvents()
	EUDEndInfLoop()

from config import outfname
LoadMap("base.scx")
SaveMap(outfname, main)
