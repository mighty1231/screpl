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

'''
Option:
    Grid 8 / 16 / 32 / 64
Mode:
    Point mode (LT, RT, RD, LD)
    Side mode (Left, Top, Right, Bottom)
    Move
'''

# global variables
_POINT_LT = 0
_POINT_RT = 1
_POINT_RB = 2
_POINT_LB = 3
_SIDE_L = 4
_SIDE_T = 5
_SIDE_R = 6
_SIDE_B = 7
_MOVE = 8
py_modes = [ # py means it is python variable
    _POINT_LT, _POINT_RT, _POINT_RB, _POINT_LB,
    _SIDE_L, _SIDE_T, _SIDE_R, _SIDE_B, _MOVE
]
py_modes_string = [
    "POINT_LT", "POINT_RT", "POINT_RB", "POINT_LB",
    "SIDE_L", "SIDE_T", "SIDE_R", "SIDE_B", "MOVE",
]

frame = EUDVariable()

# available modes
prev_available_modes = EUDArray(len(py_modes))
cur_available_modes = EUDArray(len(py_modes))

# just move
cur_mode = EUDVariable(-1)
is_holding = EUDVariable(0)

# mouse pointers
prev_mX, prev_mY = EUDCreateVariables(2)
cur_mX, cur_mY = EUDCreateVariables(2)

# location information
target, cur_epd = EUDCreateVariables(2)
le, te, re, be = EUDCreateVariables(4)
prev_lv, prev_tv, prev_rv, prev_bv = EUDCreateVariables(4)
cur_lv, cur_tv, cur_rv, cur_bv = EUDCreateVariables(4)


class LocationEditorApp(Application):
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
            prev_available_modes[i] = 0
        is_holding << 1

    def evaluateAvailableModes(self):
        '''
        _POINT_LT
        _POINT_RT
        _POINT_RB
        _POINT_LB
        _SIDE_L
        _SIDE_T
        _SIDE_R
        _SIDE_B
        _MOVE
        '''
        DoActions([
            SetMemoryEPD(EPD(cur_available_modes) + i, SetTo, 0)
                for i in range(len(py_modes))
        ])

        # point
        dlx = cur_mX - cur_lv
        drx = cur_mX - cur_rv
        dty = cur_mY - cur_tv
        dby = cur_mY - cur_bv
        limit = 16
        for d in [dlx, drx, dty, dby]:
            if EUDIf()(d >= 0x7FFFFFFF):
                d << -d
            EUDEndIf()

        if EUDIf()([dlx <= limit, dty <= limit]):
            DoActions(SetMemoryEPD(EPD(cur_available_modes), SetTo, 1))
        EUDEndIf()
        if EUDIf()([drx <= limit, dty <= limit]):
            DoActions(SetMemoryEPD(EPD(cur_available_modes)+1, SetTo, 1))
        EUDEndIf()
        if EUDIf()([drx <= limit, dby <= limit]):
            DoActions(SetMemoryEPD(EPD(cur_available_modes)+2, SetTo, 1))
        EUDEndIf()
        if EUDIf()([dlx <= limit, dby <= limit]):
            DoActions(SetMemoryEPD(EPD(cur_available_modes)+3, SetTo, 1))
        EUDEndIf()

        is_l_x_r = EUDVariable()
        is_t_y_b = EUDVariable()
        if EUDIf()([cur_lv <= cur_mX, cur_mX <= cur_rv]):
            is_l_x_r << 1
        if EUDElse()():
            is_l_x_r << 0
        EUDEndIf()
        if EUDIf()([cur_tv <= cur_mY, cur_mY <= cur_bv]):
            is_t_y_b << 1
        if EUDElse()():
            is_t_y_b << 0
        EUDEndIf()

        Logger.format("L %D R %D T %D B %D", dlx, drx, dty, dby)
        Logger.format("inside X %D Y %D", is_l_x_r, is_t_y_b)
        Logger.format("l x r %D %D %D", cur_lv, cur_mX, cur_rv)
        Logger.format("t y b %D %D %D", cur_tv, cur_mY, cur_bv)

        if EUDIf()([is_t_y_b.Exactly(1), dlx <= limit]):
            DoActions(SetMemoryEPD(EPD(cur_available_modes)+4, SetTo, 1))
        EUDEndIf()
        if EUDIf()([is_l_x_r.Exactly(1), dty <= limit]):
            DoActions(SetMemoryEPD(EPD(cur_available_modes)+5, SetTo, 1))
        EUDEndIf()
        if EUDIf()([is_t_y_b.Exactly(1), drx <= limit]):
            DoActions(SetMemoryEPD(EPD(cur_available_modes)+6, SetTo, 1))
        EUDEndIf()
        if EUDIf()([is_l_x_r.Exactly(1), dby <= limit]):
            DoActions(SetMemoryEPD(EPD(cur_available_modes)+7, SetTo, 1))
        EUDEndIf()

        if EUDIf()([is_t_y_b.Exactly(1), is_l_x_r.Exactly(1)]):
            DoActions(SetMemoryEPD(EPD(cur_available_modes)+8, SetTo, 1))
        EUDEndIf()


    def loop(self):
        global cur_mode
        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
            EUDReturn()
        if EUDElseIf()(appManager.keyPress("L")):
            appManager.startApplication(Logger)
            EUDReturn()
        EUDEndIf()

        # new mouse values and location
        pos = appManager.getMousePositionXY()
        cur_mX << pos[0]
        cur_mY << pos[1]
        cur_lv << f_dwread_epd(le)
        cur_tv << f_dwread_epd(te)
        cur_rv << f_dwread_epd(re)
        cur_bv << f_dwread_epd(be)

        # set modes!
        if EUDIf()(appManager.mouseLClick()):
            '''
            evaluate available modes
            if available modes not changed,
                set next mode, find available starts from the previous mode
            else:
                set next mode, find available starts from mode = 0
            '''
            self.evaluateAvailableModes()

            if EUDIf()(f_memcmp(prev_available_modes, cur_available_modes, 4*len(py_modes)) == 0):
                cur_mode += 1
            if EUDElse()():
                cur_mode << 0
            EUDEndIf()

            if EUDIf()([MemoryEPD(EPD(cur_available_modes)+i, Exactly, 0) \
                    for i in range(len(py_modes))]):
                # not available
                cur_mode << -1
            if EUDElse()():
                # choose available
                if EUDLoopN()(len(py_modes)):
                    Trigger(
                        conditions=cur_mode.Exactly(len(py_modes)),
                        actions=cur_mode.SetNumber(0)
                    )
                    if EUDIf()(cur_available_modes[cur_mode] == 1):
                        EUDBreak()
                    EUDEndIf()
                    cur_mode += 1
                EUDEndLoopN()
            EUDEndIf()

            f_repmovsd_epd(EPD(prev_available_modes), EPD(cur_available_modes), len(py_modes))
        EUDEndIf()

        # get new mode
        if EUDIf()(appManager.keyDown(keymap["editor"]["hold"])):
            is_holding << 1
            prev_mX << cur_mX
            prev_mY << cur_mY
        if EUDElseIf()(appManager.keyUp(keymap["editor"]["hold"])):
            is_holding << 0
        EUDEndIf()

        # functions
        if EUDIf()(is_holding == 1):
            dX = cur_mX - prev_mX
            dY = cur_mY - prev_mY
            if EUDIf()([dX == 0, dY == 0]):
                # nothing to make change
                pass
            if EUDElse()():
                # If values are preserved among frames, make a change.
                # Otherwise, make mode clear.
                #    It may due to a trigger that handles the location.
                if EUDIf()([
                            prev_lv == cur_lv,
                            prev_tv == cur_tv,
                            prev_rv == cur_rv,
                            prev_bv == cur_bv,
                        ]):

                    # @TODO other modes...
                    if EUDIf()(cur_mode == _POINT_LT):
                        DoActions([
                            SetMemoryEPD(le, SetTo, cur_mX),
                            SetMemoryEPD(te, SetTo, cur_mY),
                        ])
                    if EUDElseIf()(cur_mode == _POINT_RT):
                        DoActions([
                            SetMemoryEPD(re, SetTo, cur_mX),
                            SetMemoryEPD(te, SetTo, cur_mY),
                        ])
                    if EUDElseIf()(cur_mode == _POINT_RB):
                        DoActions([
                            SetMemoryEPD(re, SetTo, cur_mX),
                            SetMemoryEPD(be, SetTo, cur_mY),
                        ])
                    if EUDElseIf()(cur_mode == _POINT_LB):
                        DoActions([
                            SetMemoryEPD(le, SetTo, cur_mX),
                            SetMemoryEPD(be, SetTo, cur_mY),
                        ])
                    if EUDElseIf()(cur_mode == _SIDE_L):
                        DoActions([SetMemoryEPD(le, SetTo, cur_mX)])
                    if EUDElseIf()(cur_mode == _SIDE_T):
                        DoActions([SetMemoryEPD(te, SetTo, cur_mY)])
                    if EUDElseIf()(cur_mode == _SIDE_R):
                        DoActions([SetMemoryEPD(re, SetTo, cur_mX)])
                    if EUDElseIf()(cur_mode == _SIDE_B):
                        DoActions([SetMemoryEPD(be, SetTo, cur_mY)])
                    if EUDElseIf()(cur_mode == _MOVE):
                        DoActions([
                            SetMemoryEPD(ee, Add, vv) for ee, vv in zip(
                                [le, te, re, be],
                                [dX, dY, dX, dY]
                            )
                        ])
                    EUDEndIf()
                if EUDElse()():
                    # value changed!
                    # other trigger may handled the location
                    is_holding << 0

                    # @TODO report
                EUDEndIf()
            EUDEndIf()
        EUDEndIf()

        # update new value
        for vv, ee in zip(                            \
                [prev_lv, prev_tv, prev_rv, prev_bv], \
                [le, te, re, be]):
            vv << f_dwread_epd(ee)
        prev_mX << cur_mX
        prev_mY << cur_mY


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
        for i in range(len(py_modes)):
            if EUDIf()(cur_mode == i):
                writer.write_f(py_modes_string[i])
            EUDEndIf()
        if EUDIf()(is_holding == 1):
            writer.write_f(" Holding...")
        EUDEndIf()
        writer.write(ord('\n'))

        for i in range(len(py_modes)):
            if EUDIf()(cur_available_modes[i]):
                writer.write_f(py_modes_string[i] + " ")
            EUDEndIf()
        writer.write_f("\n")

        writer.write_f("Left %D\n", cur_lv)
        writer.write_f("Right %D\n", cur_rv)
        writer.write_f("Top %D\n", cur_tv)
        writer.write_f("Bottom %D\n", cur_bv)

        writer.write(0)

    @AppCommand([argEncNumber])
    def setSizeX(self, value):
        lv, rv = f_dwread_epd(le), f_dwread_epd(re)
        sz = rv - lv
        f_dwadd_epd(re, value-sz)

    @AppCommand([argEncNumber])
    def setSizeY(self, value):
        tv, bv = f_dwread_epd(te), f_dwread_epd(be)
        sz = bv - tv
        f_dwadd_epd(be, value-sz)

