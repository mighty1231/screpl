from eudplib import *
from . import appManager
"""
type
CUnit, CSprite
bool, u8, u16, s16, u32, s32
Target, Position, point
UnitMovementState
rect

Point<T, int scale>: T x, y;

Target: Position pt; CUnit *pUnit;
Position: Point<s16, 1>
point: s32 x, y;
rect: s16 l, t, r, b;
points: s16 x, y;
"""
writer = appManager.getWriter()

@EUDFunc
def cw_bool(epd, off):
    writer.write_bool(f_bread_epd(epd, off))

@EUDFunc
def cw_u8(epd, off):
    writer.write_u8(f_bread_epd(epd, off))

@EUDFunc
def cw_u16(epd, off):
    writer.write_u16(f_wread_epd(epd, off))

@EUDFunc
def cw_s16(epd, off):
    writer.write_s16(f_wread_epd(epd, off))

@EUDFunc
def cw_u32(epd, off):
    writer.write_u32(f_dwread_epd(epd))

@EUDFunc
def cw_s32(epd, off):
    writer.write_s32(f_dwread_epd(epd))

@EUDFunc
def cw_CUnit(epd, off):
    writer.write_f("CUnit(%H)", f_cunitread_epd(epd))

@EUDFunc
def cw_CSprite(epd, off):
    writer.write_f("CSprite(%H)", f_dwread_epd(epd))

@EUDFunc
def cw_Position(epd, off):
    x, y = f_wread_epd(epd, 0), f_wread_epd(epd, 2)
    writer.write_f("Position(x=%I16d, y=%I16d)", x, y)

@EUDFunc
def cw_Target(epd, off):
    x, y = f_wread_epd(epd, 0), f_wread_epd(epd, 2)
    cunit = f_cunitread_epd(epd + 1)
    writer.write_f("Target(x=%I16d, y=%I16d, pUnit=CUnit(%H))",
        x, y, cunit)

@EUDFunc
def cw_point(epd, off):
    x, y = f_dwread_epd(epd), f_dwread_epd(epd + 1)
    writer.write_f("point(x=%I32d, y=%I32d)", x, y)

@EUDFunc
def cw_points(epd, off):
    x, y = f_wread_epd(epd, 0), f_wread_epd(epd, 2)
    writer.write_f("points(x=%I16d, y=%I16d)", x, y)

@EUDFunc
def cw_rect(epd, off):
    l = f_wread_epd(epd, 0)
    t = f_wread_epd(epd, 2)
    r = f_wread_epd(epd+1, 0)
    b = f_wread_epd(epd+1, 2)
    writer.write_f("rect(l=%I16d, t=%I16d, r=%I16d, b=%I16d",
        l, t, r, b)

class Entry(ExprProxy):
    def __init__(self, offset, write_f, name, comments = None):
        _off_epd, _off = divmod(offset, 4)
        _name = EPDConstString(name)
        if comments is None:
            _comments = EPD(0)
        else:
            _comments = EPDConstString(comments)

        baseobj = EUDVArrayData(5)([
            _off_epd, _off, write_f, _name, _comments
        ])
        super().__init__(baseobj)
        self.dontFlatten = True
        self._epd = EPD(self)
        self._attrmap = {
            "off_epd": 0, "off": 1, "write_f": 2, "name": 3, "comments": 4
        }

    def __getattr__(self, attr):
        if attr in self._attrmap:
            return self._get(self._attrmap[attr])
        return super().__getattr__(self, attr)

    def __setattr__(self, attr, value):
        if attr in self._attrmap:
            self._set(self._attrmap[attr], value)
        else:
            super().__setattr__(self, attr, value)

    def _get(self, i):
        # This function is hand-optimized
        r = EUDVariable()
        vtproc = Forward()
        nptr = Forward()
        a0, a2 = Forward(), Forward()

        SeqCompute([
            (EPD(vtproc + 4), SetTo, self + 72 * i),
            (EPD(a0 + 16), SetTo, self._epd + (18 * i + 344 // 4)),
            (EPD(a2 + 16), SetTo, self._epd + (18 * i + 1)),
        ])

        vtproc << RawTrigger(
            nextptr=0,
            actions=[
                a0 << SetDeaths(0, SetTo, EPD(r.getValueAddr()), 0),
                a2 << SetDeaths(0, SetTo, nptr, 0),
            ]
        )

        nptr << NextTrigger()
        return r

    def set(self, i, value):
        # This function is hand-optimized
        a0, t = Forward(), Forward()
        SeqCompute([
            (EPD(a0 + 16), bt.SetTo, self._epd + (18 * i + 348 // 4)),
            (EPD(a0 + 20), bt.SetTo, value),
        ])
        t << bt.RawTrigger(
            actions=[
                a0 << bt.SetDeaths(0, bt.SetTo, 0, 0),
            ]
        )

cu_members = [
    Entry(0x000, cw_CUnit, "prev"),
    Entry(0x004, cw_CUnit, "next"),
    Entry(0x008, cw_s32, "hitPoints",
            "Hit points of unit, note that the displayed value in broodwar is ceil(healthPoints/256)"),
    Entry(0x00C, cw_CSprite, "sprite"),
    Entry(0x010, cw_Target, "moveTarget",
            "The position or unit to move to. It is NOT an order target."),
    Entry(0x018, cw_Position, "nextMovementWaypoint",
            "The next way point in the path the unit is following to get to its destination.\n"     + \
            "Equal to moveToPos for air units since they don't need to navigate around buildings\n" + \
            "or other units."),
    Entry(0x01C, cw_Position, "nextTargetWaypoint", "The desired position"),
    Entry(0x020, cw_u8, "movementFlags", "Flags specifying movement type - defined in BW#MovementFlags."),
    Entry(0x021, cw_u8, "currentDirection1", "The current direction the unit is facing"),
    Entry(0x022, cw_u8, "flingyTurnRadius"),
    Entry(0x023, cw_u8, "velocityDirection1",
            "This usually only differs from the currentDirection field for units that can accelerate\n"    + \
            "and travel in a different direction than they are facing. For example Mutalisks can change\n" + \
            "the direction they are facing faster than then can change the direction they are moving."),
    Entry(0x024, cw_u16, "flingyID"),
    Entry(0x027, cw_u8, "flingyMovementType"),
    Entry(0x028, cw_Position, "position", "Current position of the unit"),
    Entry(0x02C, cw_point, "halt", "@todo Unknown // Either this or current_speed is officially called \"xDX, xDY\" (no POINT struct)")
    Entry(0x034, cw_u32, "flingyTopSpeed"),
    Entry(0x038, cw_s32, "current_speed1"),
    Entry(0x03C, cw_s32, "current_speed2"),
    Entry(0x040, cw_point, "current_speed"),
    Entry(0x048, cw_u16, "flingyAcceleration"),
    Entry(0x04A, cw_u8, "currentDirection2"),
    Entry(0x04B, cw_u8, "velocityDirection2", "pathing related, gets this value from Path::unk_1A?"),
    Entry(0x04C, cw_u8, "playerID", "Specification of owner of this unit."),
    Entry(0x04D, cw_u8, "orderID", "Specification of type of order currently given."),
    Entry(0x04E, cw_u8, "orderState",
            "Additional order info (mostly unknown, wander property investigated so far)  // officially \"ubActionState\"\n" + \
            "0x01  Moving/Following Order\n" + \
            "0x02  No collide (Larva)?\n" + \
            "0x04  Harvesting? Working?\n" + \
            "0x08  Constructing Stationary\n" + \
            "Note: I don't actually think these are flags"),
    Entry(0x04F, cw_u8, "orderSignal",
            "0x01  Update building graphic/state\n" + \
            "0x02  Casting spell\n" + \
            "0x04  Reset collision? Always enabled for hallucination...\n" + \
            "0x10  Lift/Land state"),
    Entry(0x050, cw_u16, "orderUnitType", "officially \"uwFoggedTarget\""),
    Entry(0x054, cw_u8, "mainOrderTimer", "A timer for orders, example: time left before minerals are harvested"),
    Entry(0x055, cw_u8, "groundWeaponCooldown"),
    Entry(0x056, cw_u8, "airWeaponCooldown"),
    Entry(0x057, cw_u8, "spellCooldown"),
    Entry(0x058, cw_Target, "orderTarget", "officially called ActionFocus"),
    Entry(0x060, cw_u32, "shieldPoints", "BW shows this value/256, possibly not u32?"),
    Entry(0x064, cw_u16, "unitType", "Specifies the type of unit."),

    Entry(0x068, cw_CUnit, "previousPlayerUnit"),
    Entry(0x06C, cw_CUnit, "nextPlayerUnit"),
    Entry(0x070, cw_CUnit, "subUnit"),
    Entry(0x07C, cw_CUnit, "autoTargetUnit", "The auto-acquired target (Note: This field is actually used for different targets internally, especially by the AI)"),
    Entry(0x080, cw_CUnit, "connectedUnit", "Addon is connected to building (addon has conntected building, but not in other direction  (officially \"pAttached\")"),
    Entry(0x084, cw_u8, "orderQueueCount", "@todo Verify   // officially \"ubQueuedOrders\""),
    Entry(0x085, cw_u8, "orderQueueTimer", "counts/cycles down from from 8 to 0 (inclusive). See also 0x122."),
    Entry(0x086, cw_u8, "_unknown_0x086", "pathing related?"),
    Entry(0x087, cw_u8, "attackNotifyTimer", "Prevent \"Your forces are under attack.\" on every attack"),

    # 0x8A: ?
    Entry(0x088, cw_u16, "previousUnitType", "Stores the type of the unit prior to being morphed/constructed"),
    Entry(0x08A, cw_u8, "lastEventTimer", "countdown that stops being recent when it hits 0 "),
    Entry(0x08A, cw_u8, "lastEventTimer", "countdown that stops being recent when it hits 0 "),
    Entry(0x08B, cw_u8, "lastEventColor", "17 = was completed (train, morph), 174 = was attacked"),
    Entry(0x08C, cw_u16, "_unused_0x08C", "might have originally been RGB from lastEventColor"),
    Entry(0x08E, cw_u8, "rankIncrease", "Adds this value to the unit's base rank"),
    Entry(0x08F, cw_u8, "killCount", "Killcount"),
    Entry(0x090, cw_u8, "lastAttackingPlayer", "the player that last attacked this unit"),
    Entry(0x091, cw_u8, "secondaryOrderTimer"),
    Entry(0x092, cw_u8, "AIActionFlag", "Internal use by AI only"),
    Entry(0x093, cw_u8, "userActionFlags",
            "some flags that change when the user interacts with the unit\n" + \
            "2 = issued an order, 3 = interrupted an order, 4 = self destructing"),

    Entry(0x094, cw_u16, "currentButtonSet", "The u16 is a guess, used to be u8"),
    Entry(0x096, cw_bool, "isCloaked"),
    Entry(0x097, cw_u8, "movementState",
            "A value based on conditions related to pathing\n" + \
            "0x00: UM_Init\n"          + \
            "0x01: UM_InitSeq\n"       + \
            "0x02: UM_Lump\n"          + \
            "0x03: UM_Turret\n"        + \
            "0x04: UM_Bunker\n"        + \
            "0x05: UM_BldgTurret\n"    + \
            "0x06: UM_Hidden\n"        + \
            "0x07: UM_Flyer\n"         + \
            "0x08: UM_FakeFlyer\n"     + \
            "0x09: UM_AtRest\n"        + \
            "0x0A: UM_Dormant\n"       + \
            "0x0B: UM_AtMoveTarget\n"  + \
            "0x0C: UM_CheckIllegal\n"  + \
            "0x0D: UM_MoveToLegal\n"   + \
            "0x0E: UM_LumpWannabe\n"   + \
            "0x0F: UM_FailedPath\n"    + \
            "0x10: UM_RetryPath\n"     + \
            "0x11: UM_StartPath\n"     + \
            "0x12: UM_UIOrderDelay\n"  + \
            "0x13: UM_TurnAndStart\n"  + \
            "0x14: UM_FaceTarget\n"    + \
            "0x15: UM_NewMoveTarget\n" + \
            "0x16: UM_AnotherPath\n"   + \
            "0x17: UM_Repath\n"        + \
            "0x18: UM_RepathMovers\n"  + \
            "0x19: UM_FollowPath\n"    + \
            "0x1A: UM_ScoutPath\n"     + \
            "0x1B: UM_ScoutFree\n"     + \
            "0x1C: UM_FixCollision\n"  + \
            "0x1D: UM_WaitFree\n"      + \
            "0x1E: UM_GetFree\n"       + \
            "0x1F: UM_SlidePrep\n"     + \
            "0x20: UM_SlideFree\n"     + \
            "0x21: UM_ForceMoveFree\n" + \
            "0x22: UM_FixTerrain\n"    + \
            "0x23: UM_TerrainSlide\n"
        )

    Entry(0x098, cw_u16, "buildQueue[0]", "Queue of units to build. Note that it doesn't begin with index 0, but with #buildQueueSlot index."),
    Entry(0x09A, cw_u16, "buildQueue[1]", "Queue of units to build. Note that it doesn't begin with index 0, but with #buildQueueSlot index."),
    Entry(0x09C, cw_u16, "buildQueue[2]", "Queue of units to build. Note that it doesn't begin with index 0, but with #buildQueueSlot index."),
    Entry(0x09E, cw_u16, "buildQueue[3]", "Queue of units to build. Note that it doesn't begin with index 0, but with #buildQueueSlot index."),
    Entry(0x0A0, cw_u16, "buildQueue[4]", "Queue of units to build. Note that it doesn't begin with index 0, but with #buildQueueSlot index."),
    Entry(0x0A2, cw_u16, "energy", "Energy Points   // officially \"xwMagic\""),
    Entry(0x0A4, cw_u8, "buildQueueSlot", "Index of active unit in #buildQueue. "),
    Entry(0x0A5, cw_u8, "uniquenessIdentifier", "A byte used to determine uniqueness of the unit"),
    Entry(0x0A6, cw_u8, "secondaryOrderID", "(Build addon verified) @todo verify (Cloak, Build, ExpandCreep suggested by EUDDB)"),
    Entry(0x0A7, cw_u8, "buildingOverlayState", "0 means the building has the largest amount of fire/blood"),
    Entry(0x0A8, cw_u16, "hpGain", "hp gained on construction or repair"),
    Entry(0x0AA, cw_u16, "shieldGain", "Shield gain on construction"),
    Entry(0x0AC, cw_u16, "remainingBuildTime", "Remaining bulding time; This is also the timer for powerups (flags) to return to their original location."),
    Entry(0x0AE, cw_u16, "previousHP", "The HP of the unit before it changed (example Drone->Hatchery, the Drone's HP will be stored here)"),

    # union on 0xC0 ~ 0xCF
    Entry(0x0C0, cw_u8, "vulture.spiderMineCount"),
    Entry(0x0C0, cw_CUnit, "carrier/reaver.pInHanger", "first child inside the hanger"),
    Entry(0x0C4, cw_CUnit, "carrier/reaver.pOutHanger", "first child outside the hanger"),
    Entry(0x0C8, cw_u8, "carrier/reaver.inHangerCount", "number inside the hanger (used for scarab count)"),
    Entry(0x0C9, cw_u8, "carrier/reaver.outHangerCount", "number outside the hanger"),
    Entry(0x0C0, cw_CUnit, "fighter/scarab.parent"),
    Entry(0x0C4, cw_CUnit, "fighter/scarab.prev"),
    Entry(0x0C8, cw_CUnit, "fighter/scarab.next"),
    Entry(0x0CC, cw_bool, "fighter/scarab.inHanger"),
    Entry(0x0C8, cw_u32, "beacon.flagSpawnFrame"),
    Entry(0x0C0, cw_CUnit, "building.addon"),
    Entry(0x0C4, cw_u16, "building.addonBuildType"),
    Entry(0x0C6, cw_u16, "building.upgradeResearchTime"),
    Entry(0x0C8, cw_u8, "building.techType"),
    Entry(0x0C9, cw_u8, "building.upgradeType"),
    Entry(0x0CA, cw_u8, "building.larvaTimer"),
    Entry(0x0CB, cw_u8, "building.landingTimer"),
    Entry(0x0CC, cw_u8, "building.creepTimer"),
    Entry(0x0CD, cw_u8, "building.upgradeLevel"),
    Entry(0x0C0, cw_CUnit, "worker.pPowerup"),
    Entry(0x0C4, cw_points, "worker.targetResource"),
    Entry(0x0C8, cw_CUnit, "worker.targetResourceUnit"),
    Entry(0x0CC, cw_u16, "worker.repairResourceLossTimer"),
    Entry(0x0CE, cw_bool, "worker.isCarryingSomething", "There is a \"ubIsHarvesting\" somewhere"),
    Entry(0x0CF, cw_u8, "worker.resourceCarryCount"),

    # union on 0xD0 ~ 0xDB
    Entry(0x0D0, cw_u16, "resource.resourceCount", "amount of resources"),
    Entry(0x0D2, cw_u8, "resource.resourceIscript"),
    Entry(0x0D3, cw_u8, "resource.gatherQueueCount"),
    Entry(0x0D4, cw_CUnit, "resource.nextGatherer", "pointer to the next workerunit waiting in line to gather"),
    Entry(0x0D8, cw_u8, "resource.resourceGroup"),
    Entry(0x0D9, cw_u8, "resource.resourceBelongsToAI"),
    Entry(0x0D0, cw_CUnit, "nydus.exit", "connected nydus canal"),
    Entry(0x0D0, cw_CSprite, "pylon.pPowerTemplate"),
    Entry(0x0D0, cw_CUnit, "silo.pNuke", "attacked nuke // offical name"),
    Entry(0x0D4, cw_bool, "silo.bReady", "offical name"),
    Entry(0x0D0, cw_rect, "hatchery.harvestValue", "wtf???"),
    Entry(0x0D0, cw_points, "powerup.origin"),
    Entry(0x0D0, cw_CUnit, "gatherer.harvestTarget"),
    Entry(0x0D4, cw_CUnit, "gatherer.prevHarvestUnit", "When there is a gather conflict"),
    Entry(0x0D8, cw_CUnit, "gatherer.nextHarvestUnit"),

    Entry(0x0DC, cw_u32, "statusFlags"),
    Entry(0x0E0, cw_u8, "resourceType", "Resource being held by worker: 1 = gas, 2 = ore"),
    Entry(0x0E1, cw_u8, "wireframeRandomizer"),
    Entry(0x0E2, cw_u8, "secondaryOrderState"),
    Entry(0x0E3, cw_u8, "recentOrderTimer",
            "Counts down from 15 to 0 when most orders are given,\n" +  \
            "or when the unit moves after reaching a patrol location"),
    Entry(0x0E4, cw_s32, "visibilityStatus", "Flags specifying which players can detect this unit (cloaked/burrowed)"),
    Entry(0x0E8, cw_Position, "secondaryOrderPosition", "unused"),
    Entry(0x0EC, cw_CUnit, "currentBuildUnit", "tied to secondary order"),
    Entry(0x110, cw_u16, "removeTimer", "does not apply to scanner sweep"),
    Entry(0x112, cw_u16, "defenseMatrixDamage"),
    Entry(0x114, cw_u8, "defenseMatrixTimer"),
    Entry(0x115, cw_u8, "stimTimer"),
    Entry(0x116, cw_u8, "ensnareTimer"),
    Entry(0x117, cw_u8, "lockdownTimer"),
    Entry(0x118, cw_u8, "irradiateTimer"),
    Entry(0x119, cw_u8, "stasisTimer"),
    Entry(0x11A, cw_u8, "plagueTimer"),
    Entry(0x11B, cw_u8, "stormTimer"),
    Entry(0x11C, cw_CUnit, "irradiatedBy"),
    Entry(0x120, cw_u8, "irradiatePlayerID"),
    Entry(0x121, cw_u8, "parasiteFlags", "bitmask identifying which players have parasited this unit"),
    Entry(0x122, cw_u8, "cycleCounter", "counts/cycles up from 0 to 7 (inclusive). See also 0x85."),
    Entry(0x123, cw_bool, "isBlind"),
    Entry(0x124, cw_u8, "maelstromTimer"),
    Entry(0x125, cw_u8, "_unused_0x125", "?? Might be afterburner timer or ultralisk roar timer"),
    Entry(0x126, cw_u8, "acidSporeCount"),
    Entry(0x127, cw_u8, "acidSporeTime[0]"),
    Entry(0x128, cw_u8, "acidSporeTime[1]"),
    Entry(0x129, cw_u8, "acidSporeTime[2]"),
    Entry(0x12A, cw_u8, "acidSporeTime[3]"),
    Entry(0x12B, cw_u8, "acidSporeTime[4]"),
    Entry(0x12C, cw_u8, "acidSporeTime[5]"),
    Entry(0x12D, cw_u8, "acidSporeTime[6]"),
    Entry(0x12E, cw_u8, "acidSporeTime[7]"),
    Entry(0x12F, cw_u8, "acidSporeTime[8]"),
    Entry(0x14C, cw_u8, "_repulseUnknown", "@todo Unknown"),
    Entry(0x14D, cw_u8, "repulseAngle", "updated only when air unit is being pushed"),
    Entry(0x14E, cw_u8, "bRepMtxX", "(mapsizex/1.5 max)"),
    Entry(0x14F, cw_u8, "bRepMtxY", "(mapsizex/1.5 max)"),
]
