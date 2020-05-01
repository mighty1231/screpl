''' PATTERN MODE
* feature

1. Effect player - default: Computer player
2. Effect unit - (loc maximum size~) scourge, overlord, battlecruiser
3. Obstacle unit - Terran Machine Shop, Psi Emitter
4. Start / End location
5. runner : Zerg Zergling
6. turbo mode: EUDTurbo, Turbo

(trig_actions~...)

1. Output to bridge - select death variable (player * unit)
 * macro - BOMB
 * macro - Obstacle

macro bomb(location):
 - CreateUnit(1, specified_unit, effect_player, location)
 - KillUnitAtLocation(All, unit, location, effect_p)
 - KillUnitAtLocation(All, runner, location, runnerforce)

macro obstacle(location):
 - CreateUnit(1, unit, effect_player, location)

macro obstacledestruct(location):
 - KillUnit(1, unit, effect_player, location)

# feature
pattern test

Expected TUI
 1. Bound Editor - PATTERN MODE
 2. [<<(Q)] [<(W)] {focused_pattern_id}/{p_count} [>(E)] [>>(R)]
 3. Append(A), Insert(I), Copy(C), Delete(D), Test(T)
 4. Wait Value(,.): 1
 5. 
 6. Total {num_actions} actions, press 'P' to detailed action editor
 7. Mode(M): Bomb, Obstacle, ObstacleDestruct
 8. LClick to select location, RClick to confirm
 9. Location UI
'''

from repl import Application
from repl.resources.table.tables import getLocationNameEPDPointer
from ...location.rect import drawRectangle
from . import appManager, superuser, focused_pattern_id
from .detail import DetailedActionApp

MACRO_BOMB = 0
MACRO_OBSTACLE = 1
MACRO_OBSTACLEDESTRUCT = 2
MACRO_UNDEFINED = 3
macro_mode = EUDVariable(0)

cur_wait_value = EUDVariable()

# choose location
chosen_location = EUDVariable(0)

# draw location
frame = EUDVariable(0)
FRAME_PERIOD = 24

@EUDFunc
def evaluateLocations():
    posX, posY = appManager.getMousePositionXY()

    cur = EUDVariable()
    cur << chosen_location


    # prepare the loop (chosen_location+1, chosen_location+2, ..., chosen_location)
    le = EPD(0x58DC60 - 0x14) + (0x14 // 4) * cur
    te = le + 1
    re = le + 2
    be = le + 3

    la, ta, ra, ba = [Forward() for _ in range(4)]
    SeqCompute([
        # player field of SetMemory
        (EPD(la) + 4, SetTo, le),
        (EPD(ta) + 4, SetTo, te),
        (EPD(ra) + 4, SetTo, re),
        (EPD(ba) + 4, SetTo, be),

        # value field of SetMemory
        (EPD(la) + 5, SetTo, posX),
        (EPD(ta) + 5, SetTo, posY),
        (EPD(ra) + 5, SetTo, posX),
        (EPD(ba) + 5, SetTo, posY),
    ])

    if EUDInfLoop()():
        DoActions([
            cur.AddNumber(1),
            SetMemoryEPD(EPD(la) + 4, Add, 0x14 // 4),
            SetMemoryEPD(EPD(ta) + 4, Add, 0x14 // 4),
            SetMemoryEPD(EPD(ra) + 4, Add, 0x14 // 4),
            SetMemoryEPD(EPD(ba) + 4, Add, 0x14 // 4),
        ])
        Trigger(
            conditions = cur.Exactly(256),
            actions = [
                cur.SetNumber(1),
                SetMemoryEPD(EPD(la) + 4, SetTo, EPD(0x58DC60)),
                SetMemoryEPD(EPD(ta) + 4, SetTo, EPD(0x58DC60) + 1),
                SetMemoryEPD(EPD(ra) + 4, SetTo, EPD(0x58DC60) + 2),
                SetMemoryEPD(EPD(ba) + 4, SetTo, EPD(0x58DC60) + 3),
            ]
        )

        # check mouse positions are inside the location
        if EUDIf()([
                    la << MemoryEPD(0, AtMost, 0),
                    ta << MemoryEPD(0, AtMost, 0),
                    ra << MemoryEPD(0, AtLeast, 0),
                    ba << MemoryEPD(0, AtLeast, 0),
                ]):
            EUDBreak()
        EUDEndIf()

        # no location satisfies the condition
        if EUDIf()([chosen_location.Exactly(0), cur.Exactly(255)]):
            chosen_location << 0
            EUDbreak()
        EUDEndIf()
        if EUDIf()(cur == chosen_location):
            chosen_location << 0
            EUDBreak()
        EUDEndIf()
    EUDEndInfLoop()


def focusPatternID(new_id):
    if EUDIfNot()(new_id >= p_count):
        focused_pattern_id << new_id
        cur_wait_value << p_waitValue[focused_pattern_id]
    EUDEndIf()

def insertPattern():
    # p_count-1 -> p_count
    # focused_pattern_id -> focused_pattern_id+1
    i = EUDVariable()
    array_epd = p_actionArrayEPD[p_count]
    i << p_count-1
    ii = i + 1
    if EUDInfLoop()():
        p_waitValue[ii] = p_waitValue[i]
        p_actionCount[ii] = p_actionCount[i]
        p_actionArrayEPD[ii] = p_actionArrayEPD[i]
        EUDBreakIf(i == focused_pattern_id)
        DoActions([i.SubtractNumber(1), ii.SubtractNumber(1)])
    EUDEndInfLoop()
    p_actionArrayEPD[i] = array_epd

    DoActions([
        SetMemoryEPD(EPD(p_waitValue) + focused_pattern_id, SetTo, 1),
        SetMemoryEPD(EPD(p_actionCount) + focused_pattern_id, SetTo, 0),
    ])
    cur_wait_value << 1
    p_count += 1

def deletePattern():
    if EUDIfNot()(p_count == 1):
        if EUDIf()(focused_pattern_id == p_count - 1):
            DoActions([
                p_count.SubtractNumber(1),
                focused_pattern_id.SubtractNumber(1)
            ])
        if EUDElse()():
            # focused_pattern_id <- focused_pattern_id+1
            # p_count-2 << p_count-1
            i = EUDVariable()
            array_epd = p_actionArrayEPD[focused_pattern_id]
            i << focused_pattern_id
            ii = i + 1
            if EUDInfLoop()():
                EUDBreakIf(i == p_count-1)
                p_waitValue[i] = p_waitValue[ii]
                p_actionCount[i] = p_actionCount[ii]
                p_actionArrayEPD[i] = p_actionArrayEPD[ii]
                DoActions([i.AddNumber(1), ii.AddNumber(1)])
            EUDEndInfLoop()
            p_actionArrayEPD[i] = array_epd
            p_count -= 1
        EUDEndIf()
    EUDEndIf()
    cur_wait_value << p_waitValue[focused_pattern_id]

def appendPattern():
    DoActions([
        SetMemoryEPD(EPD(p_waitValue) + p_count, SetTo, 1),
        SetMemoryEPD(EPD(p_actionCount) + p_count, SetTo, 0),
    ])
    focused_pattern_id << p_count
    cur_wait_value << 1
    p_count += 1

class PatternApp(Application):
    def onInit(self):
        cur_wait_value << p_waitValue[focused_pattern_id]
        chosen_location << 0

    def loop(self):
        if EUDIf()(appManager.keyPress('Q')):
            focusPatternID(0)
        if EUDElseIf()(appManager.keyPress('W')):
            focusPatternID(focused_pattern_id - 1)
        if EUDElseIf()(appManager.keyPress('E')):
            focusPatternID(focused_pattern_id + 1)
        if EUDElseIf()(appManager.keyPress('R')):
            focusPatternID(p_count-1)
        if EUDElseIf()(appManager.keyPress('A')):
            appendPattern()
        if EUDElseIf()(appManager.keyPress('I')):
            insertPattern()
        if EUDElseIf()(appManager.keyPress('C')):
            copyPattern()
        if EUDElseIf()(appManager.keyPress('D')):
            deletePattern()
        if EUDElseIf()(appManager.keyPress('T')):
            cleanScreen()
            executePattern(focused_pattern_id)
        if EUDElseIf()(appManager.keyPress('P')):
            appManager.startApplication(DetailedActionApp)
        if EUDElseIf()(appManager.keyPress('M')):
            macro_mode += 1
            Trigger(
                conditions=macro_mode.Exactly(MACRO_UNDEFINED),
                actions=macro_mode.SetNumber(0)
            )
        if EUDElseIf()(appManager.keyPress(',')):
            if EUDIfNot()(cur_wait_value == 1):
                DoActions([
                    cur_wait_value.SubtractNumber(1),
                    SetMemoryEPD(EPD(p_waitValue) + focused_pattern_id, Subtract, 1),
                ])
            EUDEndIf()
        if EUDElseIf()(appManager.keyPress('.')):
            DoActions([
                cur_wait_value.AddNumber(1),
                SetMemoryEPD(EPD(p_waitValue) + focused_pattern_id, Add, 1),
            ])
        if EUDElseIf()(appManager.LClick()):
            evaluateLocations()
        if EUDElseIf()(appManager.RClick()):
            # confirm
            if EUDIfNot()(chosen_location.Exactly(0)):
                if EUDIf()(macro_mode.Exactly(MACRO_BOMB)):
                    ADD_MACRO_BOMB
                if EUDElseIf()(macro_mode.Exactly(MACRO_OBSTACLE)):
                    ADD_MACRO_OBSTACLE
                if EUDElse()(macro_mode.Exactly(MACRO_OBSTACLEDESTRUCT)):
                    ADD_MACRO_OBSTACLEDESTRUCT
                EUDEndIf()
            EUDEndIf()
        EUDEndIf()

        # draw rectangle
        if EUDIfNot()(chosen_location.Exactly(0)):
            drawRectangle(chosen_location, frame, FRAME_PERIOD)

            # graphical set
            DoActions(frame.AddNumber(1))
            if EUDIf()(frame == FRAME_PERIOD):
                DoActions(frame.SetNumber(0))
            EUDEndIf()
        EUDEndIf()
        appManager.requestUpdate()

    def print(self, writer):
        writer.write_f("Bound Editor - PATTERN MODE\n")
        writer.write_f("[<<(Q)] [<(W)] %D / %D [>(E)] [>>(R)]\n",
            focused_pattern_id+1, p_count)
        writer.write_f("Append(A), Insert(I), Copy(C), Delete(D), Test(T)\n")
        writer.write_f("Wait value(,.): %D\n", cur_wait_value)

        writer.write_f("Mode(M): ")
        if EUDIf()(macro_mode == MACRO_BOMB):
            writer.write(0x11)
        if EUDElse()():
            writer.write(2)
        EUDEndIf()
        writer.write_f("Bomb ")
        if EUDIf()(macro_mode == MACRO_OBSTACLE):
            writer.write(0x11)
        if EUDElse()():
            writer.write(2)
        EUDEndIf()
        writer.write_f("Obstacle ")
        if EUDIf()(macro_mode == MACRO_OBSTACLEDESTRUCT):
            writer.write(0x11)
        if EUDElse()():
            writer.write(2)
        EUDEndIf()
        writer.write_f("ObstacleDestruct\n")

        writer.write_f("LClick to change location, RClick to confirm the location\n")

        if EUDIf()(chosen_location.Exactly(0)):
            writer.write_f("Not available")
        if EUDElse()():
            writer.write_f("Chosen Location: %E", getLocationNameEPDPointer(chosen_location))
        EUDEndIf()
        writer.write_f("\n")
