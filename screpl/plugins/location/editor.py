# -*- coding: utf-8 -*-
from eudplib import *

from screpl.apps.chatreader import ChatReaderApp
from screpl.core.appcommand import AppCommand
from screpl.core.application import Application
from screpl.encoder.const import ArgEncNumber
from screpl.resources.table.tables import get_locationname_epd
from screpl.utils.string import f_memcmp_epd

from screpl.main import get_app_manager

from .rect import draw_rectangle

app_manager = get_app_manager()

'''
Option:
    Grid 1 / 8 / 16 / 32
Tool
    Create tool
    Edit tool
Edit Mode:
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
py_editmodes = [ # py means it is python variable
    _POINT_LT, _POINT_RT, _POINT_RB, _POINT_LB,
    _SIDE_L, _SIDE_T, _SIDE_R, _SIDE_B, _MOVE
]

gridvalues = [1, 8, 16, 32]
gridmasks = [0xFFFFFFFF, 0xFFFFFFF8, 0xFFFFFFF0, 0xFFFFFFE0]

# available modes
prev_available_editmodes = EUDArray(len(py_editmodes))
cur_available_editmodes = EUDArray(len(py_editmodes))

# modes
cur_editmode = EUDVariable(-1)
is_holding = EUDVariable(0)

cur_gridmode = EUDVariable(0)
cur_gridval = EUDVariable(1)
cur_gridmask = EUDVariable(0xFFFFFFFF)

# mouse pointers
prev_mX, prev_mY = EUDCreateVariables(2)
cur_mX, cur_mY = EUDCreateVariables(2)

# location information
target, cur_epd = EUDCreateVariables(2)
le, te, re, be = EUDCreateVariables(4)
prev_lv, prev_tv, prev_rv, prev_bv = EUDCreateVariables(4)
cur_lv, cur_tv, cur_rv, cur_bv = EUDCreateVariables(4)

DISPMODE_MAIN = 0
DISPMODE_MANUAL = 1
v_dispmode = EUDVariable()

TOOL_CREATE = 0
TOOL_EDIT = 1
v_tool = EUDVariable()

class LocationEditorApp(Application):
    fields = []

    @staticmethod
    def set_target(location):
        target << location
        cur_epd << EPD(0x58DC60 - 0x14) + (0x14 // 4) * location
        le << cur_epd
        te << cur_epd + 1
        re << cur_epd + 2
        be << cur_epd + 3

    def on_init(self):
        v_dispmode << DISPMODE_MAIN
        for i in range(len(py_editmodes)):
            prev_available_editmodes[i] = 0
        cur_editmode << -1
        is_holding << 0

    def evaluate_available_editmodes(self):
        DoActions([
            SetMemoryEPD(EPD(cur_available_editmodes) + i, SetTo, 0)
                for i in range(len(py_editmodes))
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
            DoActions(SetMemoryEPD(EPD(cur_available_editmodes), SetTo, 1))
        EUDEndIf()
        if EUDIf()([drx <= limit, dty <= limit]):
            DoActions(SetMemoryEPD(EPD(cur_available_editmodes)+1, SetTo, 1))
        EUDEndIf()
        if EUDIf()([drx <= limit, dby <= limit]):
            DoActions(SetMemoryEPD(EPD(cur_available_editmodes)+2, SetTo, 1))
        EUDEndIf()
        if EUDIf()([dlx <= limit, dby <= limit]):
            DoActions(SetMemoryEPD(EPD(cur_available_editmodes)+3, SetTo, 1))
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

        if EUDIf()([is_t_y_b.Exactly(1), dlx <= limit]):
            DoActions(SetMemoryEPD(EPD(cur_available_editmodes)+4, SetTo, 1))
        EUDEndIf()
        if EUDIf()([is_l_x_r.Exactly(1), dty <= limit]):
            DoActions(SetMemoryEPD(EPD(cur_available_editmodes)+5, SetTo, 1))
        EUDEndIf()
        if EUDIf()([is_t_y_b.Exactly(1), drx <= limit]):
            DoActions(SetMemoryEPD(EPD(cur_available_editmodes)+6, SetTo, 1))
        EUDEndIf()
        if EUDIf()([is_l_x_r.Exactly(1), dby <= limit]):
            DoActions(SetMemoryEPD(EPD(cur_available_editmodes)+7, SetTo, 1))
        EUDEndIf()

        if EUDIf()([is_t_y_b.Exactly(1), is_l_x_r.Exactly(1)]):
            DoActions(SetMemoryEPD(EPD(cur_available_editmodes)+8, SetTo, 1))
        EUDEndIf()


    def loop(self):
        global cur_editmode, cur_gridmode

        # new mouse values and location
        pos = app_manager.get_mouse_position()
        cur_mX << pos[0]
        cur_mY << pos[1]
        cur_lv << f_dwread_epd(le)
        cur_tv << f_dwread_epd(te)
        cur_rv << f_dwread_epd(re)
        cur_bv << f_dwread_epd(be)
        is_holding << 0

        if EUDIf()(app_manager.key_press("ESC")):
            app_manager.request_destruct()
        if EUDElseIf()(app_manager.key_press("G", hold=["LCTRL"])):
            cur_gridmode += 1
            Trigger(
                conditions=[cur_gridmode == len(gridvalues)],
                actions=[cur_gridmode.SetNumber(0)]
            )
            EUDSwitch(cur_gridmode)
            for i, (v, m) in enumerate(zip(gridvalues, gridmasks)):
                EUDSwitchCase()(i)
                DoActions([cur_gridval.SetNumber(v),
                           cur_gridmask.SetNumber(m)])
                EUDBreak()
            EUDEndSwitch()
        if EUDElseIf()(app_manager.key_down("F1")):
            v_dispmode << DISPMODE_MANUAL
        if EUDElseIf()(app_manager.key_up("F1")):
            v_dispmode << DISPMODE_MAIN
        if EUDElseIf()(app_manager.key_press("E", hold=["LCTRL"])):
            v_tool << 1 - v_tool
        EUDEndIf()

        if EUDIf()(v_tool == TOOL_CREATE):
            if EUDIf()(app_manager.mouse_ldrag(sync=[cur_mX, cur_mY])):
                if EUDIf()(cur_gridval == 1):
                    cur_lv << prev_mX
                    cur_tv << prev_mY
                    cur_rv << cur_mX
                    cur_bv << cur_mY
                if EUDElse()():
                    cur_lv << f_bitand(prev_mX + (cur_gridval // 2), cur_gridmask)
                    cur_tv << f_bitand(prev_mY + (cur_gridval // 2), cur_gridmask)
                    cur_rv << f_bitand(cur_mX + (cur_gridval // 2), cur_gridmask)
                    cur_bv << f_bitand(cur_mY + (cur_gridval // 2), cur_gridmask)
                EUDEndIf()
                f_dwwrite_epd(le, cur_lv)
                f_dwwrite_epd(te, cur_tv)
                f_dwwrite_epd(re, cur_rv)
                f_dwwrite_epd(be, cur_bv)
            if EUDElseIf()(app_manager.mouse_lpress(sync=[cur_mX, cur_mY])):
                prev_mX << cur_mX
                prev_mY << cur_mY
            EUDEndIf()
        if EUDElse()():
            if EUDIf()(app_manager.mouse_lclick(sync=[cur_mX, cur_mY])):
                '''
                evaluate available modes
                if available modes not changed,
                    set next mode, find available starts from the previous mode
                else:
                    set next mode, find available starts from mode = 0
                '''
                self.evaluate_available_editmodes()

                if EUDIf()(f_memcmp_epd(EPD(prev_available_editmodes),
                                        EPD(cur_available_editmodes),
                                        len(py_editmodes)) == 0):
                    cur_editmode += 1
                if EUDElse()():
                    cur_editmode << 0
                EUDEndIf()

                if EUDIf()([MemoryEPD(EPD(cur_available_editmodes)+i, Exactly, 0) \
                        for i in range(len(py_editmodes))]):
                    # not available
                    cur_editmode << -1
                if EUDElse()():
                    # choose available
                    if EUDLoopN()(len(py_editmodes)):
                        Trigger(
                            conditions=cur_editmode.Exactly(len(py_editmodes)),
                            actions=cur_editmode.SetNumber(0)
                        )
                        if EUDIf()(cur_available_editmodes[cur_editmode] == 1):
                            EUDBreak()
                        EUDEndIf()
                        cur_editmode += 1
                    EUDEndLoopN()
                EUDEndIf()

                f_repmovsd_epd(EPD(prev_available_editmodes),
                               EPD(cur_available_editmodes),
                               len(py_editmodes))
            if EUDElseIf()(app_manager.key_down("H",
                                                sync=[cur_mX, cur_mY])):
                is_holding << 1
                prev_mX << cur_mX
                prev_mY << cur_mY
            if EUDElseIf()(app_manager.key_press("H",
                                                 sync=[cur_mX, cur_mY])):
                is_holding << 1
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
                    if EUDIf()([prev_lv == cur_lv,
                                prev_tv == cur_tv,
                                prev_rv == cur_rv,
                                prev_bv == cur_bv]):

                        # @TODO other modes...
                        grid_X, grid_Y = EUDCreateVariables(2)
                        grid_X << (cur_mX // cur_gridval) * cur_gridval
                        grid_Y << (cur_mY // cur_gridval) * cur_gridval

                        if EUDIf()(cur_editmode == _POINT_LT):
                            DoActions([
                                SetMemoryEPD(le, SetTo, grid_X),
                                SetMemoryEPD(te, SetTo, grid_Y),
                            ])
                        if EUDElseIf()(cur_editmode == _POINT_RT):
                            DoActions([
                                SetMemoryEPD(re, SetTo, grid_X),
                                SetMemoryEPD(te, SetTo, grid_Y),
                            ])
                        if EUDElseIf()(cur_editmode == _POINT_RB):
                            DoActions([
                                SetMemoryEPD(re, SetTo, grid_X),
                                SetMemoryEPD(be, SetTo, grid_Y),
                            ])
                        if EUDElseIf()(cur_editmode == _POINT_LB):
                            DoActions([
                                SetMemoryEPD(le, SetTo, grid_X),
                                SetMemoryEPD(be, SetTo, grid_Y),
                            ])
                        if EUDElseIf()(cur_editmode == _SIDE_L):
                            DoActions([SetMemoryEPD(le, SetTo, grid_X)])
                        if EUDElseIf()(cur_editmode == _SIDE_T):
                            DoActions([SetMemoryEPD(te, SetTo, grid_Y)])
                        if EUDElseIf()(cur_editmode == _SIDE_R):
                            DoActions([SetMemoryEPD(re, SetTo, grid_X)])
                        if EUDElseIf()(cur_editmode == _SIDE_B):
                            DoActions([SetMemoryEPD(be, SetTo, grid_Y)])
                        if EUDElseIf()(cur_editmode == _MOVE):
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
            for vv, ee in zip([prev_lv, prev_tv, prev_rv, prev_bv],
                              [le, te, re, be]):
                vv << f_dwread_epd(ee)
            prev_mX << cur_mX
            prev_mY << cur_mY
        EUDEndIf()

        #####################
        #   Draw Location   #
        #####################

        # draw location with "Scanner Sweep"
        draw_rectangle(target)

        app_manager.request_update()

    def print(self, writer):
        if EUDIf()(v_dispmode == DISPMODE_MAIN):
            writer.write_f("\x16Location Editor #%D %:location; Grid: %D / "
                           "Press F1 to get manual\n",
                           target, (target, ), cur_gridval)

            if EUDIf()(v_tool == TOOL_CREATE):
                writer.write_f("Create tool - update location with just drag\n")
            if EUDElseIf()(v_tool == TOOL_EDIT):
                writer.write_f("Edit tool")
                if EUDIf()(is_holding == 1):
                    writer.write_f(" Holding...\n")
                if EUDElse()():
                    writer.write_f(" Move mouse cursor with holding 'H'\n")
                EUDEndIf()

                # note: without \x0D, some of those characters are handled
                #       as color code in SC
                writer.write_f(
                    "%C\x0D┎%C\x0D━%C\x0D┒\n"
                    "%C\x0D┃%C\x0D╋%C\x0D┃\n"
                    "%C\x0D┖%C\x0D━%C\x0D┚\n",
                    EUDTernary(cur_editmode==_POINT_LT)(0x11)(0x16),
                    EUDTernary(cur_editmode==_SIDE_T)(0x11)(0x16),
                    EUDTernary(cur_editmode==_POINT_RT)(0x11)(0x16),
                    EUDTernary(cur_editmode==_SIDE_L)(0x11)(0x16),
                    EUDTernary(cur_editmode==_MOVE)(0x11)(0x16),
                    EUDTernary(cur_editmode==_SIDE_R)(0x11)(0x16),
                    EUDTernary(cur_editmode==_POINT_LB)(0x11)(0x16),
                    EUDTernary(cur_editmode==_SIDE_B)(0x11)(0x16),
                    EUDTernary(cur_editmode==_POINT_RB)(0x11)(0x16))
            EUDEndIf()

            writer.write_f(
                "\x16Left %D\n"
                "Right %D\n"
                "Top %D\n"
                "Bottom %D\n",
                cur_lv, cur_rv, cur_tv, cur_bv)

            if EUDIf()([cur_lv <= 0x80000000, cur_rv <= 0x80000000]):
                if EUDIfNot()(cur_lv <= cur_rv):
                    writer.write_f("\x06X-FLIPPED\n")
                EUDEndIf()
                if EUDIfNot()(cur_tv <= cur_bv):
                    writer.write_f("\x06Y-FLIPPED\n")
                EUDEndIf()
            EUDEndIf()
        if EUDElse()():
            writer.write_f(
                "\x16Location Editor Manual\n"
                "Press CTRL+G to change grid size (1, 8, 16, 32)\n"
                "Press CTRL+E to change tool\n"
                "Creator tool creates small location with dragging\n"
                "Editor tool updates specific component of location\n"
                "Chat sw(##) to set width with given number\n"
                "Chat sh(##) to set height with given number\n"
                "Chat sf(##) to set flag with given number\n"
                "Chat cn() to update the name of location\n")
        EUDEndIf()

        writer.write(0)

    @AppCommand([ArgEncNumber])
    def sw(self, value):
        lv, rv = f_dwread_epd(le), f_dwread_epd(re)
        sz = rv - lv
        f_dwadd_epd(re, value-sz)

    @AppCommand([ArgEncNumber])
    def sh(self, value):
        tv, bv = f_dwread_epd(te), f_dwread_epd(be)
        sz = bv - tv
        f_dwadd_epd(be, value-sz)

    @AppCommand([ArgEncNumber])
    def sf(self, flag):
        f_wwrite_epd(cur_epd+4, 2, flag)

    @AppCommand([])
    def cn(self):
        ChatReaderApp.set_return_epd(get_locationname_epd(target))
        app_manager.start_application(ChatReaderApp)
