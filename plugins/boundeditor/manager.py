from eudplib import *

from repl import Application, f_raiseError
from . import appManager, computer_player, timer_unit, superuser
from .option import OptionApp
from .pattern import PatternApp
from .testmode import TestPatternApp

'''
Global Variable
1. Effect player - default: Computer player
2. Effect unit - (loc maximum size~) scourge, overlord, battlecruiser
3. Obstacle unit - Terran Machine Shop, Psi Emitter
4. Start / End location
5. runner force: Force1
6. runner unit: Zerg Zergling

*****
variable, only output - Death var 

*****
Location plugin
 * location chooser (on screen locations)
    - track mouse, select
 * add new location w/ name

*****
Mode
1. Test mode (some EUDLightVariable)
  - Start - create "runner"
2. Edit location
3. Edit pattern
(trig_actions~...)
  - [<<] [<] $PATTERN [>] [>>]
  - Append, Insert, Copy, Delete

Function
1. Output to bridge - select death variable (player * unit)
 * macro - BOMB
 * macro - Obstacle

Effect action ~ unit, location
 * Create and Kill
 * Create
 * Kill
 * Remove

Obstacle action ~ unit, location
 * Create
 * Kill
 * Remove

Runner action
 * Kill
 * Move ~ unit, location, location

ENTITY: wait(N) or TriggerAction
MODE: None, EUDTurbo, Turbo

############### STRUCTURE ###################
memory structure
round 1: action count, wait value, 
round N: 
'''

class BoundManagerApp(Application):
    def loop(self):
        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
            EUDReturn()
        if EUDElseIf()(appManager.keyPress("O")):
            appManager.startApplication(OptionApp)
        if EUDElseIf()(appManager.keyPress("P")):
            appManager.startApplication(PatternApp)
        if EUDElseIf()(appManager.keyPress("T")):
            appManager.startApplication(TestPatternApp)
        EUDEndIf()

    def print(self, writer):
        writer.write_f("\x16Bound Editor Manager\n")
        writer.write(0)

    @AppCommand([])
    def maphack(self):
        le = EPD(0x58DC60)
        te = EPD(0x58DC60) + 1
        re = EPD(0x58DC60) + 2
        be = EPD(0x58DC60) + 3

        lv, tv, rv, bv = [f_dwread_epd(ee) for ee in [le, te, re, be]]

        mapw = appManager.getMapWidth()
        maph = appManager.getMapHeight()

        actions = []
        for y in range(256, maph * 32, 512):
            actions.append(SetMemoryEPD(te, SetTo, y))
            actions.append(SetMemoryEPD(be, SetTo, y))

            for x in range(256, mapw * 32, 512):
                actions.append(SetMemoryEPD(le, SetTo, x))
                actions.append(SetMemoryEPD(re, SetTo, x))
                actions.append(CreateUnit(1, "Map Revealer", 1, superuser))
        DoActions(actions)

        for ee, vv in zip([le, te, re, be], [lv, tv, rv, bv]):
            f_dwwrite_epd(ee, vv)

