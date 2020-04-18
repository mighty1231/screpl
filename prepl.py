from eudplib import *

def beforeTriggerExec():
	# loading settings
	pid = 0 # default as P1
	if 'superuser' in settings:
		su = playerMap.get(settings['superuser'], settings['superuser'])
		pid = EncodePlayer(su)

	if pid not in range(7):
		raise RuntimeError('Superuser in REPL should be one of P1~P8')

	from repl import getAppManager, AppCommand

	manager = getAppManager(superuser = pid)
	from repl.app import LocationApp, REPL

	@AppCommand([])
	def openloc(self):
		manager.openApplication(LocationApp)

	REPL.addCommand('openloc', openloc)

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
