from eudplib import *
from repl import (
    Application,
    AppTypedMethod,
    AppCommand,
    argEncNumber
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

target, frame = EUDCreateVariables(2)
mouseX, mouseY = EUDCreateVariables(2)
previous_mode = EUDArray(len(py_modes))

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

    def onInit(self):
        frame << 0

    def getNextMode(self):
        pass

    def loop(self):
        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
            EUDReturn()
        EUDEndIf()

        pos = appManager.getMousePositionXY()
        mouseX << pos[0]
        mouseY << pos[1]

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
        '''
        writer.write_f()
        '''
        pass

