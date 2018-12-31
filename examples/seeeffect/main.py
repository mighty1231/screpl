from eudplib import *

def beforeTriggerExec():
	from repl import (
		REPL, EUDCommand, argEncNumber, argEncUnit, RegisterCommand
	)

	DoActions(SetDeaths(203151, SetTo, 1, 0))
	REPL(superuser=P1).execute() # The position of this function does not matter

	# SEE EFFECT
	UNIT = EUDVariable(initval = EncodeUnit("Terran Marine"))
	COUNT = EUDVariable(initval = 1)
	DoActions([
		CreateUnit(COUNT, UNIT, "Anywhere", P1),
		KillUnit(UNIT, P1)
	])

	# Make function that modifies variables - UNIT and CNT
	@EUDCommand([argEncUnit, argEncNumber])
	def SeeEffect(u, n):
		UNIT << u
		COUNT << n

	# Register command for REPL
	RegisterCommand("effect", SeeEffect)
