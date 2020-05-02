''' PATTERN MODE
Expected TUI
 1. Bound Editor - PATTERN MODE
 2. [<<(Q)] [<(W)] {focused_pattern_id}/{p_count} [>(E)] [>>(R)]
 3. Append(A), Insert(I), Delete(D), Test(T)
 4. Wait Value(,.): 1
 5. 
 6. Total {num_actions} actions, press 'P' to detailed action editor
 7. Mode(M): Bomb, Obstacle, ObstacleDestruct
 8. LClick to select location, press 'N' to confirm
 9. Chosen location
'''

from eudplib import *

from repl import Application, writeLocation, encodeAction_epd, f_raiseWarning
from ..location.rect import drawRectangle
from .detail import DetailedActionApp
from . import (
    appManager,
    MAX_ACTION_COUNT,
    focused_pattern_id,
    g_effectplayer,
    g_effectunit_1,
    g_effectunit_2,
    g_effectunit_3,
    g_obstacle_unit,
    g_start_location,
    g_runner_force,
    g_runner_unit,
    OBSTACLE_CREATEPATTERN_KILL,
    OBSTACLE_CREATEPATTERN_REMOVE,
    OBSTACLE_CREATEPATTERN_ALIVE,
    OBSTACLE_CREATEPATTERN_END,
    g_obstacle_createpattern,
    OBSTACLE_DESTRUCTPATTERN_KILL,
    OBSTACLE_DESTRUCTPATTERN_REMOVE,
    OBSTACLE_DESTRUCTPATTERN_END,
    g_obstacle_destructpattern,
    writePlayer,
    p_count,
    p_waitValue,
    p_actionCount,
    p_actionArrayEPD,
    executePattern
)

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
        # memory field of Memory
        (EPD(la) + 1, SetTo, le),
        (EPD(ta) + 1, SetTo, te),
        (EPD(ra) + 1, SetTo, re),
        (EPD(ba) + 1, SetTo, be),

        # value field of Memory
        (EPD(la) + 2, SetTo, posX),
        (EPD(ta) + 2, SetTo, posY),
        (EPD(ra) + 2, SetTo, posX),
        (EPD(ba) + 2, SetTo, posY),
    ])

    if EUDInfLoop()():
        DoActions([
            cur.AddNumber(1),
            SetMemoryEPD(EPD(la) + 1, Add, 0x14 // 4),
            SetMemoryEPD(EPD(ta) + 1, Add, 0x14 // 4),
            SetMemoryEPD(EPD(ra) + 1, Add, 0x14 // 4),
            SetMemoryEPD(EPD(ba) + 1, Add, 0x14 // 4),
        ])
        Trigger(
            conditions = cur.Exactly(256),
            actions = [
                cur.SetNumber(1),
                SetMemoryEPD(EPD(la) + 1, SetTo, EPD(0x58DC60)),
                SetMemoryEPD(EPD(ta) + 1, SetTo, EPD(0x58DC60) + 1),
                SetMemoryEPD(EPD(ra) + 1, SetTo, EPD(0x58DC60) + 2),
                SetMemoryEPD(EPD(ba) + 1, SetTo, EPD(0x58DC60) + 3),
            ]
        )

        # check mouse positions are inside the location
        if EUDIf()([
                    la << Memory(0, AtMost, 0),
                    ta << Memory(0, AtMost, 0),
                    ra << Memory(0, AtLeast, 0),
                    ba << Memory(0, AtLeast, 0),
                ]):
            chosen_location << cur
            EUDReturn()
        EUDEndIf()

        # no location satisfies the condition
        if EUDIf()([chosen_location.Exactly(0), cur.Exactly(255)]):
            chosen_location << 0
            EUDReturn()
        EUDEndIf()
        if EUDIf()(cur == chosen_location):
            chosen_location << 0
            EUDReturn()
        EUDEndIf()
    EUDEndInfLoop()


def focusPatternID(new_id):
    global p_count
    if EUDIfNot()(new_id >= p_count):
        focused_pattern_id << new_id
        cur_wait_value << p_waitValue[focused_pattern_id]
    EUDEndIf()

def insertPattern():
    global p_count
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
    global p_count
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
    global p_count
    DoActions([
        SetMemoryEPD(EPD(p_waitValue) + p_count, SetTo, 1),
        SetMemoryEPD(EPD(p_actionCount) + p_count, SetTo, 0),
    ])
    focused_pattern_id << p_count
    cur_wait_value << 1
    p_count += 1

def appendAction(action):
    actionArray_epd = p_actionArrayEPD[focused_pattern_id]
    actionCount = p_actionCount[focused_pattern_id]
    if EUDIf()(actionCount == MAX_ACTION_COUNT - 1):
        f_raiseWarning("Cannot create more action")
        EUDReturn()
    EUDEndIf()

    encodeAction_epd(actionArray_epd + (actionCount * (32 // 4)), action)
    DoActions(SetMemoryEPD(EPD(p_actionCount) + focused_pattern_id, Add, 1))

class PatternApp(Application):
    def onInit(self):
        cur_wait_value << p_waitValue[focused_pattern_id]
        chosen_location << 0

    def loop(self):
        global macro_mode
        if EUDIf()(appManager.keyPress('ESC')):
            appManager.requestDestruct()
            EUDReturn()
        if EUDElseIf()(appManager.keyPress('Q')):
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
        if EUDElseIf()(appManager.keyPress('D')):
            deletePattern()
        if EUDElseIf()(appManager.keyPress('T')):
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
        if EUDElseIf()(appManager.mouseLClick()):
            evaluateLocations()
        # if EUDElseIf()(appManager.mouseRClick()):
        if EUDElseIf()(appManager.keyPress('N')):
            # confirm
            if EUDIfNot()(chosen_location.Exactly(0)):
                if EUDIf()(macro_mode.Exactly(MACRO_BOMB)):

                    # evaluate size of chosen_location
                    epd = EPD(0x58DC60 - 0x14) + (0x14 // 4) * chosen_location
                    lv = f_dwread_epd(epd)
                    tv = f_dwread_epd(epd+1)
                    rv = f_dwread_epd(epd+2)
                    bv = f_dwread_epd(epd+3)
                    sizex = rv - lv
                    sizey = bv - tv
                    minsize = EUDVariable()
                    if EUDIf()(sizex <= sizey):
                        minsize << sizex
                    if EUDElse()():
                        minsize << sizey
                    EUDEndIf()

                    effectunit = EUDVariable()
                    if EUDIf()(minsize <= 32+16):
                        effectunit << g_effectunit_1
                    if EUDElseIf()(minsize <= 32+32+16):
                        effectunit << g_effectunit_2
                    if EUDElse()():
                        effectunit << g_effectunit_3
                    EUDEndIf()

                    appendAction(CreateUnit(1, effectunit, chosen_location, g_effectplayer))
                    appendAction(KillUnitAt(1, effectunit, chosen_location, g_effectplayer))
                    # appendAction(KillUnitAt(All, g_runner_unit, chosen_location, g_runner_force))
                    appendAction(KillUnitAt(All, "(men)", chosen_location, g_runner_force))
                if EUDElseIf()(macro_mode.Exactly(MACRO_OBSTACLE)):
                    appendAction(CreateUnit(1, g_obstacle_unit, chosen_location, g_effectplayer))
                    if EUDIf()(g_obstacle_createpattern.Exactly(OBSTACLE_CREATEPATTERN_KILL)):
                        # appendAction(KillUnitAt(All, g_runner_unit, chosen_location, g_runner_force))
                        appendAction(KillUnitAt(All, "(men)", chosen_location, g_runner_force))
                    if EUDElseIf()(g_obstacle_createpattern.Exactly(OBSTACLE_CREATEPATTERN_REMOVE)):
                        # appendAction(RemoveUnitAt(All, g_runner_unit, chosen_location, g_runner_force))
                        appendAction(RemoveUnitAt(All, "(men)", chosen_location, g_runner_force))
                    EUDEndIf()
                if EUDElseIf()(macro_mode.Exactly(MACRO_OBSTACLEDESTRUCT)):
                    if EUDIf()(g_obstacle_destructpattern.Exactly(OBSTACLE_DESTRUCTPATTERN_KILL)):
                        appendAction(KillUnitAt(All, g_obstacle_unit, chosen_location, g_effectplayer))
                    if EUDElseIf()(g_obstacle_destructpattern.Exactly(OBSTACLE_DESTRUCTPATTERN_REMOVE)):
                        appendAction(RemoveUnitAt(All, g_obstacle_unit, chosen_location, g_effectplayer))
                    EUDEndIf()
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
        writer.write_f("Append(A), Insert(I), Delete(D), Test(T)\n")
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

        writer.write_f("\x02LClick to change location, RClick to confirm the location\n")

        if EUDIf()(chosen_location.Exactly(0)):
            writer.write_f("No Location is chosen")
        if EUDElse()():
            writer.write_f("Chosen location: ")
            writeLocation(chosen_location)
        EUDEndIf()
        writer.write_f("\n")
        writer.write(0)
