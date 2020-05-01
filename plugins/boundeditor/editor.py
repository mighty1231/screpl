from eudplib import *

from repl import Application, f_raiseError
from . import appManager, computer_player, timer_unit, superuser


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


def appendPattern():
    if EUDIf()(actionCount == MAX_PATTERN_COUNT - 1):
        f_raiseWarning("Cannot create more pattern")
        EUDReturn()
    EUDEndIf()
    v_patternCount += 1
    v_currentPattern << v_patternCount
    DoActions([
        SetMemoryEPD(EPD(vp_WaitValue) + v_patternCount, SetTo, 1),
        SetMemoryEPD(EPD(vp_ActionCount) + v_patternCount, SetTo, 0),
    ])


def appendAction(pattern, action):
    actionArray_epd = vp_ActionArrayEPDs[pattern]
    actionCount = vp_ActionCount[pattern]
    if EUDIf()(actionCount == MAX_ACTION_COUNT - 1):
        f_raiseWarning("Cannot create more action")
        EUDReturn()
    EUDEndIf()
    f_repmovsd_epd(
        actionArray_epd + (actionCount * (32 // 4)),
        action,
        32 // 4
    )

class BoundManagerApp(Application):
    fields = [
    ]

    def onInit(self):
        pass

    def onDestruct(self):
        pass

    def focusUnitID(self, new_unitid):
        pass

    def loop(self):
        unitid = self.unitid
        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
            EUDReturn()
        if EUDElseIf()(appManager.keyPress("F7")):
            self.focusUnitID(unitid - 1)
            appManager.requestUpdate()
        if EUDElseIf()(appManager.keyPress("F8")):
            self.focusUnitID(unitid + 1)
            appManager.requestUpdate()
        EUDEndIf()

    def print(self, writer):
        writer.write_f("\x16Bound Editor\n")

        target_unitid = self.unitid

        branch, branch_common, branch_last = [Forward() for _ in range(3)]
        cur, until = EUDCreateVariables(2)
        if EUDIf()(target_unitid == 232):
            cur << 232
            until << 232 + 1
            DoActions(SetNextPtr(branch, branch_last))
        if EUDElse()():
            quot, mod = f_div(target_unitid, 8)
            cur << quot * 8
            until << cur + 8
            DoActions(SetNextPtr(branch, branch_common))
        EUDEndIf()

        # fill contents
        written_point = Forward()
        if EUDInfLoop()():
            EUDBreakIf(cur >= until)

            if EUDIf()(cur == target_unitid):
                writer.write(0x11) # orange
            if EUDElse()():
                writer.write(0x02) # pale blue
            EUDEndIf()

            writer.write_f(" %D: ", cur)
            if EUDIf()(cur <= 227):
                stringid = off_unitsdat_UnitMapString.read(cur)

                if EUDIfNot()(stringid == 0):
                    writer.write_STR_string(stringid)
                    EUDJump(written_point)
                EUDEndIf()
            EUDEndIf()
            writer.write_f("%E", EUDGetDefaultUnitName_epd(cur))

            written_point << NextTrigger()
            writer.write(ord('\n'))

            DoActions(cur.AddNumber(1))
        EUDEndInfLoop()

        branch << RawTrigger()
        branch_last << NextTrigger()
        writer.write_f("\n" * 7)

        branch_common << NextTrigger()
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

