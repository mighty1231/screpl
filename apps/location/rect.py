from eudplib import *

from . import manager, mapw, maph

def drawRectangle(location, frame, frame_period):
    superuser = manager.superuser

    cur_epd = EPD(0x58DC60 - 0x14) + (0x14 // 4) * location
    le, te, re, de = cur_epd, cur_epd+1, cur_epd+2, cur_epd+3
    lv, tv, rv, dv = [f_dwread_epd(ee) for ee in [le, te, re, de]]

    # 0, 0, 0, 0: pass
    # size 0 -> draw '+'
    # run under each side
    #    length == 0  -> draw point
    #    length <= 32 -> draw 3 points (start, end, mid)
    #    length >  32 -> draw 5 points with interval 8 pixels
    #                    , moves length / 24 for every single frame
    #                    ((frame * length / 24) + offset) % length
    mark = lambda: DoActions(CreateUnit(1, "Scanner Sweep", location, superuser))
    end_point = Forward()

    # not a location
    EUDJumpIf(lv >= mapw * 32, end_point)
    EUDJumpIf(rv >= mapw * 32, end_point)
    EUDJumpIf(tv >= maph * 32, end_point)
    EUDJumpIf(dv >= maph * 32, end_point)

    i, end = EUDCreateVariables(2)
    if EUDIf()([lv == rv, tv == dv]):
        if EUDIfNot()([lv == 0, tv == 0]):
            # draw '+'
            i << lv - 16
            end << lv + 16
            if EUDWhile()([i <= end]):
                if EUDIf()([i > 0]):
                    f_dwwrite_epd(le, i)
                    f_dwwrite_epd(re, i)
                    mark()
                EUDEndIf()
                i += 2
            EUDEndWhile()

            f_dwwrite_epd(le, lv)
            f_dwwrite_epd(re, rv)

            i << tv - 16
            end << tv + 16
            if EUDWhile()([i <= end]):
                if EUDIf()([i > 0]):
                    f_dwwrite_epd(te, i)
                    f_dwwrite_epd(de, i)
                    mark()
                EUDEndIf()
                i += 2
            EUDEndWhile()
        EUDEndIf()
        EUDJump(end_point)
    EUDEndIf()

    length = EUDVariable()
    bias = EUDVariable()

    @EUDFunc
    def plus(bias, length, _from, _to, epd1, epd2):
        i = _from + bias
        if EUDLoopN()(5):
            f_dwwrite_epd(epd1, i)
            f_dwwrite_epd(epd2, i)
            DoActions(CreateUnit(1, "Scanner Sweep", location, superuser))

            i += 8
            if EUDIf()(i > _to):
                i -= length
            EUDEndIf()
        EUDEndLoopN()

    @EUDFunc
    def minus(bias, length, _from, _to, epd1, epd2):
        i = _from - bias
        if EUDLoopN()(5):
            f_dwwrite_epd(epd1, i)
            f_dwwrite_epd(epd2, i)
            DoActions(CreateUnit(1, "Scanner Sweep", location, superuser))

            i -= 8
            if EUDIf()(i < _to):
                i += length
            EUDEndIf()
        EUDEndLoopN()

    # horizontal lines
    if EUDIf()(lv < rv - 32):
        length << rv - lv
        bias << (frame * length) // frame_period

        f_dwwrite_epd(de, tv)
        plus(bias, length, lv, rv, le, re)

        f_dwwrite_epd(te, dv)
        f_dwwrite_epd(de, dv)
        minus(bias, length, rv, lv, le, re)
    if EUDElseIf()(lv == rv):
        f_dwwrite_epd(de, tv)
        mark()

        f_dwwrite_epd(te, dv)
        f_dwwrite_epd(de, dv)
        mark()
    if EUDElseIf()(lv > rv + 32):
        length << lv - rv
        bias << (frame * length) // frame_period

        f_dwwrite_epd(de, tv)
        minus(bias, length, lv, rv, le, re)

        f_dwwrite_epd(te, dv)
        f_dwwrite_epd(de, dv)
        plus(bias, length, rv, lv, le, re)
    if EUDElse()():
        f_dwwrite_epd(de, tv)
        mark()
        f_dwwrite_epd(re, lv)
        mark()
        f_dwwrite_epd(le, rv)
        f_dwwrite_epd(re, rv)
        mark()

        f_dwwrite_epd(te, dv)
        f_dwwrite_epd(de, dv)
        mark()
        f_dwwrite_epd(le, lv)
        mark()
        f_dwwrite_epd(re, lv)
        mark()
    EUDEndIf()

    # restore
    for epd, val in zip([le, te, re, de], [lv, tv, rv, dv]):
        f_dwwrite_epd(epd, val)

    # verical lines
    if EUDIf()(tv < dv - 32):
        length << dv - tv
        bias << (frame * length) // frame_period

        f_dwwrite_epd(le, rv)
        plus(bias, length, tv, dv, te, de)

        f_dwwrite_epd(re, lv)
        f_dwwrite_epd(le, lv)
        minus(bias, length, dv, tv, te, de)
    if EUDElseIf()(tv  > dv + 32):
        length << tv - dv
        bias << (frame * length) // frame_period

        f_dwwrite_epd(le, rv)
        minus(bias, length, tv, dv, te, de)

        f_dwwrite_epd(re, lv)
        f_dwwrite_epd(le, lv)
        plus(bias, length, dv, tv, te, de)
    if EUDElseIf()(tv == dv):
        f_dwwrite_epd(re, lv)
        mark()

        f_dwwrite_epd(le, rv)
        f_dwwrite_epd(re, rv)
        mark()
    if EUDElse()():
        f_dwwrite_epd(re, lv)
        mark()
        f_dwwrite_epd(de, tv)
        mark()
        f_dwwrite_epd(te, dv)
        f_dwwrite_epd(de, dv)
        mark()

        f_dwwrite_epd(le, rv)
        f_dwwrite_epd(re, rv)
        mark()
        f_dwwrite_epd(te, tv)
        mark()
        f_dwwrite_epd(de, tv)
        mark()
    EUDEndIf()


    # restore location
    end_point << NextTrigger()
    for epd, val in zip([le, te, re, de], [lv, tv, rv, dv]):
        f_dwwrite_epd(epd, val)
