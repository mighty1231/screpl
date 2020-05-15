from eudplib import *
from repl import EPDConstString, StaticStruct
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
    writer.write_f("rect(l=%I16d, t=%I16d, r=%I16d, b=%I16d)",
        l, t, r, b)

class CUnitMemberEntry(StaticStruct):
    fields = [
        'off_epd',
        'off',
        ('write_f', EUDFuncPtr(2, 0)),
        'name',
        'comments',
        'activated'
    ]

    @staticmethod
    def data(offset, write_f, name, comments = None):
        off_epd, off = divmod(offset, 4)
        name = EPDConstString(name)
        write_f = EUDFuncPtr(2, 0)(write_f)
        if comments is None:
            comments = EPD(0)
        else:
            comments = EPDConstString(comments)

        entry = CUnitMemberEntry.initializeWith(
            off_epd,
            off,
            write_f,
            name,
            comments,
            1
        )
        return entry

cu_members = EUDArray([
    CUnitMemberEntry.data(0x000, cw_CUnit, "prev"),
    CUnitMemberEntry.data(0x004, cw_CUnit, "next"),
    CUnitMemberEntry.data(0x008, cw_s32, "hitPoints",
            "Hit points of unit, note that the displayed value in broodwar is ceil(healthPoints/256)"),
    CUnitMemberEntry.data(0x00C, cw_CSprite, "sprite"),
    CUnitMemberEntry.data(0x010, cw_Target, "moveTarget",
            "The position or unit to move to. It is NOT an order target."),
    CUnitMemberEntry.data(0x018, cw_Position, "nextMovementWaypoint",
            "The next way point in the path the unit is following to get to its destination.\n"     + \
            "Equal to moveToPos for air units since they don't need to navigate around buildings\n" + \
            "or other units."),
    CUnitMemberEntry.data(0x01C, cw_Position, "nextTargetWaypoint", "The desired position"),
    CUnitMemberEntry.data(0x020, cw_u8, "movementFlags", "Flags specifying movement type - defined in BW#MovementFlags."),
    CUnitMemberEntry.data(0x021, cw_u8, "currentDirection1", "The current direction the unit is facing"),
    CUnitMemberEntry.data(0x022, cw_u8, "flingyTurnRadius"),
    CUnitMemberEntry.data(0x023, cw_u8, "velocityDirection1",
            "This usually only differs from the currentDirection field for units that can accelerate\n"    + \
            "and travel in a different direction than they are facing. For example Mutalisks can change\n" + \
            "the direction they are facing faster than then can change the direction they are moving."),
    CUnitMemberEntry.data(0x024, cw_u16, "flingyID"),
    CUnitMemberEntry.data(0x027, cw_u8, "flingyMovementType"),
    CUnitMemberEntry.data(0x028, cw_Position, "position", "Current position of the unit"),
    CUnitMemberEntry.data(0x02C, cw_point, "halt", "@todo Unknown // Either this or current_speed is officially called \"xDX, xDY\" (no POINT struct)"),
    CUnitMemberEntry.data(0x034, cw_u32, "flingyTopSpeed"),
    CUnitMemberEntry.data(0x038, cw_s32, "current_speed1"),
    CUnitMemberEntry.data(0x03C, cw_s32, "current_speed2"),
    CUnitMemberEntry.data(0x040, cw_point, "current_speed"),
    CUnitMemberEntry.data(0x048, cw_u16, "flingyAcceleration"),
    CUnitMemberEntry.data(0x04A, cw_u8, "currentDirection2"),
    CUnitMemberEntry.data(0x04B, cw_u8, "velocityDirection2", "pathing related, gets this value from Path::unk_1A?"),
    CUnitMemberEntry.data(0x04C, cw_u8, "playerID", "Specification of owner of this unit."),
    CUnitMemberEntry.data(0x04D, cw_u8, "orderID", "Specification of type of order currently given."),
    CUnitMemberEntry.data(0x04E, cw_u8, "orderState",
            "Additional order info (mostly unknown, wander property investigated so far)  // officially \"ubActionState\"\n" + \
            "0x01  Moving/Following Order\n" + \
            "0x02  No collide (Larva)?\n" + \
            "0x04  Harvesting? Working?\n" + \
            "0x08  Constructing Stationary\n" + \
            "Note: I don't actually think these are flags"),
    CUnitMemberEntry.data(0x04F, cw_u8, "orderSignal",
            "0x01  Update building graphic/state\n" + \
            "0x02  Casting spell\n" + \
            "0x04  Reset collision? Always enabled for hallucination...\n" + \
            "0x10  Lift/Land state"),
    CUnitMemberEntry.data(0x050, cw_u16, "orderUnitType", "officially \"uwFoggedTarget\""),
    CUnitMemberEntry.data(0x054, cw_u8, "mainOrderTimer", "A timer for orders, example: time left before minerals are harvested"),
    CUnitMemberEntry.data(0x055, cw_u8, "groundWeaponCooldown"),
    CUnitMemberEntry.data(0x056, cw_u8, "airWeaponCooldown"),
    CUnitMemberEntry.data(0x057, cw_u8, "spellCooldown"),
    CUnitMemberEntry.data(0x058, cw_Target, "orderTarget", "officially called ActionFocus"),
    CUnitMemberEntry.data(0x060, cw_u32, "shieldPoints", "BW shows this value/256, possibly not u32?"),
    CUnitMemberEntry.data(0x064, cw_u16, "unitType", "Specifies the type of unit."),

    CUnitMemberEntry.data(0x068, cw_CUnit, "previousPlayerUnit"),
    CUnitMemberEntry.data(0x06C, cw_CUnit, "nextPlayerUnit"),
    CUnitMemberEntry.data(0x070, cw_CUnit, "subUnit"),
    CUnitMemberEntry.data(0x07C, cw_CUnit, "autoTargetUnit", "The auto-acquired target (Note: This field is actually used for different targets internally, especially by the AI)"),
    CUnitMemberEntry.data(0x080, cw_CUnit, "connectedUnit", "Addon is connected to building (addon has conntected building, but not in other direction  (officially \"pAttached\")"),
    CUnitMemberEntry.data(0x084, cw_u8, "orderQueueCount", "@todo Verify   // officially \"ubQueuedOrders\""),
    CUnitMemberEntry.data(0x085, cw_u8, "orderQueueTimer", "counts/cycles down from from 8 to 0 (inclusive). See also 0x122."),
    CUnitMemberEntry.data(0x086, cw_u8, "_unknown_0x086", "pathing related?"),
    CUnitMemberEntry.data(0x087, cw_u8, "attackNotifyTimer", "Prevent \"Your forces are under attack.\" on every attack"),

    # 0x8A: ?
    CUnitMemberEntry.data(0x088, cw_u16, "previousUnitType", "Stores the type of the unit prior to being morphed/constructed"),
    CUnitMemberEntry.data(0x08A, cw_u8, "lastEventTimer", "countdown that stops being recent when it hits 0"),
    CUnitMemberEntry.data(0x08B, cw_u8, "lastEventColor", "17 = was completed (train, morph), 174 = was attacked"),
    CUnitMemberEntry.data(0x08C, cw_u16, "_unused_0x08C", "might have originally been RGB from lastEventColor"),
    CUnitMemberEntry.data(0x08E, cw_u8, "rankIncrease", "Adds this value to the unit's base rank"),
    CUnitMemberEntry.data(0x08F, cw_u8, "killCount", "Killcount"),
    CUnitMemberEntry.data(0x090, cw_u8, "lastAttackingPlayer", "the player that last attacked this unit"),
    CUnitMemberEntry.data(0x091, cw_u8, "secondaryOrderTimer"),
    CUnitMemberEntry.data(0x092, cw_u8, "AIActionFlag", "Internal use by AI only"),
    CUnitMemberEntry.data(0x093, cw_u8, "userActionFlags",
            "some flags that change when the user interacts with the unit\n" + \
            "2 = issued an order, 3 = interrupted an order, 4 = self destructing"),

    CUnitMemberEntry.data(0x094, cw_u16, "currentButtonSet", "The u16 is a guess, used to be u8"),
    CUnitMemberEntry.data(0x096, cw_bool, "isCloaked"),
    CUnitMemberEntry.data(0x097, cw_u8, "movementState",
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
        ),
    CUnitMemberEntry.data(0x098, cw_u16, "buildQueue[0]", "Queue of units to build. Note that it doesn't begin with index 0, but with #buildQueueSlot index."),
    CUnitMemberEntry.data(0x09A, cw_u16, "buildQueue[1]", "Queue of units to build. Note that it doesn't begin with index 0, but with #buildQueueSlot index."),
    CUnitMemberEntry.data(0x09C, cw_u16, "buildQueue[2]", "Queue of units to build. Note that it doesn't begin with index 0, but with #buildQueueSlot index."),
    CUnitMemberEntry.data(0x09E, cw_u16, "buildQueue[3]", "Queue of units to build. Note that it doesn't begin with index 0, but with #buildQueueSlot index."),
    CUnitMemberEntry.data(0x0A0, cw_u16, "buildQueue[4]", "Queue of units to build. Note that it doesn't begin with index 0, but with #buildQueueSlot index."),
    CUnitMemberEntry.data(0x0A2, cw_u16, "energy", "Energy Points   // officially \"xwMagic\""),
    CUnitMemberEntry.data(0x0A4, cw_u8, "buildQueueSlot", "Index of active unit in #buildQueue."),
    CUnitMemberEntry.data(0x0A5, cw_u8, "uniquenessIdentifier", "A byte used to determine uniqueness of the unit"),
    CUnitMemberEntry.data(0x0A6, cw_u8, "secondaryOrderID", "(Build addon verified) @todo verify (Cloak, Build, ExpandCreep suggested by EUDDB)"),
    CUnitMemberEntry.data(0x0A7, cw_u8, "buildingOverlayState", "0 means the building has the largest amount of fire/blood"),
    CUnitMemberEntry.data(0x0A8, cw_u16, "hpGain", "hp gained on construction or repair"),
    CUnitMemberEntry.data(0x0AA, cw_u16, "shieldGain", "Shield gain on construction"),
    CUnitMemberEntry.data(0x0AC, cw_u16, "remainingBuildTime", "Remaining bulding time; This is also the timer for powerups (flags) to return to their original location."),
    CUnitMemberEntry.data(0x0AE, cw_u16, "previousHP", "The HP of the unit before it changed (example Drone->Hatchery, the Drone's HP will be stored here)"),

    # union on 0xC0 ~ 0xCF
    CUnitMemberEntry.data(0x0C0, cw_u8, "vulture.spiderMineCount"),
    CUnitMemberEntry.data(0x0C0, cw_CUnit, "carrier/reaver.pInHanger", "first child inside the hanger"),
    CUnitMemberEntry.data(0x0C4, cw_CUnit, "carrier/reaver.pOutHanger", "first child outside the hanger"),
    CUnitMemberEntry.data(0x0C8, cw_u8, "carrier/reaver.inHangerCount", "number inside the hanger (used for scarab count)"),
    CUnitMemberEntry.data(0x0C9, cw_u8, "carrier/reaver.outHangerCount", "number outside the hanger"),
    CUnitMemberEntry.data(0x0C0, cw_CUnit, "fighter/scarab.parent"),
    CUnitMemberEntry.data(0x0C4, cw_CUnit, "fighter/scarab.prev"),
    CUnitMemberEntry.data(0x0C8, cw_CUnit, "fighter/scarab.next"),
    CUnitMemberEntry.data(0x0CC, cw_bool, "fighter/scarab.inHanger"),
    CUnitMemberEntry.data(0x0C8, cw_u32, "beacon.flagSpawnFrame"),
    CUnitMemberEntry.data(0x0C0, cw_CUnit, "building.addon"),
    CUnitMemberEntry.data(0x0C4, cw_u16, "building.addonBuildType"),
    CUnitMemberEntry.data(0x0C6, cw_u16, "building.upgradeResearchTime"),
    CUnitMemberEntry.data(0x0C8, cw_u8, "building.techType"),
    CUnitMemberEntry.data(0x0C9, cw_u8, "building.upgradeType"),
    CUnitMemberEntry.data(0x0CA, cw_u8, "building.larvaTimer"),
    CUnitMemberEntry.data(0x0CB, cw_u8, "building.landingTimer"),
    CUnitMemberEntry.data(0x0CC, cw_u8, "building.creepTimer"),
    CUnitMemberEntry.data(0x0CD, cw_u8, "building.upgradeLevel"),
    CUnitMemberEntry.data(0x0C0, cw_CUnit, "worker.pPowerup"),
    CUnitMemberEntry.data(0x0C4, cw_points, "worker.targetResource"),
    CUnitMemberEntry.data(0x0C8, cw_CUnit, "worker.targetResourceUnit"),
    CUnitMemberEntry.data(0x0CC, cw_u16, "worker.repairResourceLossTimer"),
    CUnitMemberEntry.data(0x0CE, cw_bool, "worker.isCarryingSomething", "There is a \"ubIsHarvesting\" somewhere"),
    CUnitMemberEntry.data(0x0CF, cw_u8, "worker.resourceCarryCount"),

    # union on 0xD0 ~ 0xDB
    CUnitMemberEntry.data(0x0D0, cw_u16, "resource.resourceCount", "amount of resources"),
    CUnitMemberEntry.data(0x0D2, cw_u8, "resource.resourceIscript"),
    CUnitMemberEntry.data(0x0D3, cw_u8, "resource.gatherQueueCount"),
    CUnitMemberEntry.data(0x0D4, cw_CUnit, "resource.nextGatherer", "pointer to the next workerunit waiting in line to gather"),
    CUnitMemberEntry.data(0x0D8, cw_u8, "resource.resourceGroup"),
    CUnitMemberEntry.data(0x0D9, cw_u8, "resource.resourceBelongsToAI"),
    CUnitMemberEntry.data(0x0D0, cw_CUnit, "nydus.exit", "connected nydus canal"),
    CUnitMemberEntry.data(0x0D0, cw_CSprite, "pylon.pPowerTemplate"),
    CUnitMemberEntry.data(0x0D0, cw_CUnit, "silo.pNuke", "attacked nuke // offical name"),
    CUnitMemberEntry.data(0x0D4, cw_bool, "silo.bReady", "offical name"),
    CUnitMemberEntry.data(0x0D0, cw_rect, "hatchery.harvestValue", "wtf???"),
    CUnitMemberEntry.data(0x0D0, cw_points, "powerup.origin"),
    CUnitMemberEntry.data(0x0D0, cw_CUnit, "gatherer.harvestTarget"),
    CUnitMemberEntry.data(0x0D4, cw_CUnit, "gatherer.prevHarvestUnit", "When there is a gather conflict"),
    CUnitMemberEntry.data(0x0D8, cw_CUnit, "gatherer.nextHarvestUnit"),

    CUnitMemberEntry.data(0x0DC, cw_u32, "statusFlags"),
    CUnitMemberEntry.data(0x0E0, cw_u8, "resourceType", "Resource being held by worker: 1 = gas, 2 = ore"),
    CUnitMemberEntry.data(0x0E1, cw_u8, "wireframeRandomizer"),
    CUnitMemberEntry.data(0x0E2, cw_u8, "secondaryOrderState"),
    CUnitMemberEntry.data(0x0E3, cw_u8, "recentOrderTimer",
            "Counts down from 15 to 0 when most orders are given,\n" +  \
            "or when the unit moves after reaching a patrol location"),
    CUnitMemberEntry.data(0x0E4, cw_s32, "visibilityStatus", "Flags specifying which players can detect this unit (cloaked/burrowed)"),
    CUnitMemberEntry.data(0x0E8, cw_Position, "secondaryOrderPosition", "unused"),
    CUnitMemberEntry.data(0x0EC, cw_CUnit, "currentBuildUnit", "tied to secondary order"),
    CUnitMemberEntry.data(0x110, cw_u16, "removeTimer", "does not apply to scanner sweep"),
    CUnitMemberEntry.data(0x112, cw_u16, "defenseMatrixDamage"),
    CUnitMemberEntry.data(0x114, cw_u8, "defenseMatrixTimer"),
    CUnitMemberEntry.data(0x115, cw_u8, "stimTimer"),
    CUnitMemberEntry.data(0x116, cw_u8, "ensnareTimer"),
    CUnitMemberEntry.data(0x117, cw_u8, "lockdownTimer"),
    CUnitMemberEntry.data(0x118, cw_u8, "irradiateTimer"),
    CUnitMemberEntry.data(0x119, cw_u8, "stasisTimer"),
    CUnitMemberEntry.data(0x11A, cw_u8, "plagueTimer"),
    CUnitMemberEntry.data(0x11B, cw_u8, "stormTimer"),
    CUnitMemberEntry.data(0x11C, cw_CUnit, "irradiatedBy"),
    CUnitMemberEntry.data(0x120, cw_u8, "irradiatePlayerID"),
    CUnitMemberEntry.data(0x121, cw_u8, "parasiteFlags", "bitmask identifying which players have parasited this unit"),
    CUnitMemberEntry.data(0x122, cw_u8, "cycleCounter", "counts/cycles up from 0 to 7 (inclusive). See also 0x85."),
    CUnitMemberEntry.data(0x123, cw_bool, "isBlind"),
    CUnitMemberEntry.data(0x124, cw_u8, "maelstromTimer"),
    CUnitMemberEntry.data(0x125, cw_u8, "_unused_0x125", "?? Might be afterburner timer or ultralisk roar timer"),
    CUnitMemberEntry.data(0x126, cw_u8, "acidSporeCount"),
    CUnitMemberEntry.data(0x127, cw_u8, "acidSporeTime[0]"),
    CUnitMemberEntry.data(0x128, cw_u8, "acidSporeTime[1]"),
    CUnitMemberEntry.data(0x129, cw_u8, "acidSporeTime[2]"),
    CUnitMemberEntry.data(0x12A, cw_u8, "acidSporeTime[3]"),
    CUnitMemberEntry.data(0x12B, cw_u8, "acidSporeTime[4]"),
    CUnitMemberEntry.data(0x12C, cw_u8, "acidSporeTime[5]"),
    CUnitMemberEntry.data(0x12D, cw_u8, "acidSporeTime[6]"),
    CUnitMemberEntry.data(0x12E, cw_u8, "acidSporeTime[7]"),
    CUnitMemberEntry.data(0x12F, cw_u8, "acidSporeTime[8]"),
    CUnitMemberEntry.data(0x14C, cw_u8, "_repulseUnknown", "@todo Unknown"),
    CUnitMemberEntry.data(0x14D, cw_u8, "repulseAngle", "updated only when air unit is being pushed"),
    CUnitMemberEntry.data(0x14E, cw_u8, "bRepMtxX", "(mapsizex/1.5 max)"),
    CUnitMemberEntry.data(0x14F, cw_u8, "bRepMtxY", "(mapsizex/1.5 max)"),
])
