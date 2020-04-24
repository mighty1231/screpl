from eudplib import *
from repl import (
    Application,
    AppTypedMethod,
    AppCommand,
    argEncNumber,
    Logger
)

from . import appManager, locstrings, keymap, FRAME_PERIOD
from .rect import drawRectangle

# global variables
_POINT_LT = 0
_POINT_RT = 1
_POINT_RD = 2
_POINT_LD = 3
_SIDE_L = 4
_SIDE_T = 5
_SIDE_R = 6
_SIDE_B = 7
_MOVE = 8
py_modes = [ # py means it is python variable
    _POINT_LT, _POINT_RT, _POINT_RD, _POINT_LD,
    _SIDE_L, _SIDE_T, _SIDE_R, _SIDE_B, _MOVE
]

frame = EUDVariable()


# available modes
previous_mode = EUDArray(len(py_modes))
prevX, prevY = EUDCreateVariables(2)

# location information
target, cur_epd = EUDCreateVariables(2)
le, te, re, be = EUDCreateVariables(4)
lv, tv, rv, bv = EUDCreateVariables(4)


mouseX, mouseY = EUDCreateVariables(2)

# just move
isgrabbing = EUDVariable(0)

class LocationEditorApp(Application):
    '''
    Option:
        Grid 8 / 16 / 32 / 64
    Mode:
        Point mode (LT, RT, RD, LD)
        Side mode (Left, Top, Right, Bottom)
        Move
    '''
    fields = []

    @staticmethod
    def setTarget(location):
        target << location
        cur_epd << EPD(0x58DC60 - 0x14) + (0x14 // 4) * location
        le << cur_epd
        te << cur_epd + 1
        re << cur_epd + 2
        be << cur_epd + 3

    def onInit(self):
        frame << 0
        for i in range(len(py_modes)):
            previous_mode[i] = 0
        isgrabbing << 1

    def getNextMode(self):
        pass

    def loop(self):
        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
            EUDReturn()
        EUDEndIf()

        # new mouse values and location
        pos = appManager.getMousePositionXY()
        mouseX << pos[0]
        mouseY << pos[1]
        new_values = [f_dwread_epd(ee) for ee in [le, te, re, be]]

        # get new mode
        if EUDIf()(appManager.keyDown(keymap["editor"]["hold"])):
            isgrabbing << 1
            prevX << mouseX
            prevY << mouseY
        if EUDElseIf()(appManager.keyUp(keymap["editor"]["hold"])):
            isgrabbing << 0
        EUDEndIf()

        # functions
        if EUDIf()(isgrabbing == 1):
            dX = mouseX - prevX
            dY = mouseY - prevY
            if EUDIf()([dX == 0, dY == 0]):
                # nothing to make change
                pass
            if EUDElse()():
                # If values are preserved among frames, make a change.
                # Otherwise, make mode clear.
                #    It may due to a trigger that handles the location.
                if EUDIf()([
                            lv == new_values[0],
                            tv == new_values[1],
                            rv == new_values[2],
                            bv == new_values[3],
                        ]):

                    DoActions([
                        SetMemoryEPD(ee, Add, vv) for ee, vv in zip(
                            [le, te, re, be],
                            [dX, dY, dX, dY]
                        )
                    ])

                if EUDElse()():
                    # value changed!
                    # other trigger may handled the location
                    isgrabbing << 0

                    # @TODO report
                EUDEndIf()
            EUDEndIf()
        EUDEndIf()

        # update new value
        for vv, ee in zip([lv, tv, rv, bv], [le, te, re, be]):
            vv << f_dwread_epd(ee)
        prevX << mouseX
        prevY << mouseY


        ######################
        #   Draw Locastion   #
        ######################

        # backup Scanner Sweep and prepare effect
        prev_im = f_dwread_epd(EPD(0x666160 + 2*380))
        prev_is = f_dwread_epd(EPD(0x66EC48 + 4*232))
        DoActions([
            SetMemoryX(0x666160 + 2*380, SetTo, 232, 0xFFFF),
            SetMemory(0x66EC48 + 4*232, SetTo, 250)
        ])

        # draw location with "Scanner Sweep"
        drawRectangle(target, frame, FRAME_PERIOD)

        # restore "Scanner Sweep"
        DoActions([
            RemoveUnit("Scanner Sweep", appManager.superuser),
            SetMemoryX(0x666160 + 2*380, SetTo, prev_im, 0xFFFF),
            SetMemory(0x66EC48 + 4*232, SetTo, prev_is)
        ])

        # graphical set
        DoActions(frame.AddNumber(1))
        if EUDIf()(frame == FRAME_PERIOD):
            DoActions(frame.SetNumber(0))
        EUDEndIf()
        appManager.requestUpdate()

    def print(self, writer):
        # Title, tells its editing mode
        writer.write_f("Location Editor #%D ", target)

        str_epd = locstrings[target]
        if EUDIfNot()(str_epd == 0):
            writer.write_f("'%E' ", str_epd)
        EUDEndIf()

        writer.write_f("Mode: ")
        if EUDIf()(isgrabbing == 1):
            writer.write_f("Holding...")
        EUDEndIf()
        writer.write(ord('\n'))

        writer.write_f("Left %D\n", lv)
        writer.write_f("Right %D\n", rv)
        writer.write_f("Top %D\n", tv)
        writer.write_f("Bottom %D\n", bv)

        writer.write(0)
