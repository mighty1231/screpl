from eudplib import *

from repl.core.appcommand import AppCommand
from repl.core.application import Application
from repl.encoder.const import ArgEncNumber

from . import *
from .cunitrw import cu_members, CUnitMemberEntry

v_focused = EUDVariable()

@EUDFunc
def setFocus(new_focus):
    Trigger(
        conditions = new_focus.AtLeast(0x80000000),
        actions = new_focus.SetNumber(0)
    )
    Trigger(
        conditions = new_focus.AtLeast(cu_members.length),
        actions = new_focus.SetNumber(cu_members.length - 1)
    )
    if EUDIfNot()(v_focused >= cu_members.length):
        v_focused << new_focus
        app_manager.requestUpdate()
    EUDEndIf()

class CUnitOptionApp(Application):
    def loop(self):
        if EUDIf()(app_manager.keyPress("ESC")):
            app_manager.requestDestruct()
            EUDReturn()
        if EUDElseIf()(app_manager.keyPress("F7", hold=["LCTRL"])):
            setFocus(v_focused - 8)
        if EUDElseIf()(app_manager.keyPress("F7")):
            setFocus(v_focused - 1)
        if EUDElseIf()(app_manager.keyPress("F8", hold=["LCTRL"])):
            setFocus(v_focused + 8)
        if EUDElseIf()(app_manager.keyPress("F8")):
            setFocus(v_focused + 1)
        if EUDElseIf()(app_manager.keyPress("H")):
            member = CUnitMemberEntry.cast(cu_members[v_focused])
            if EUDIf()(member.activated == 1):
                idx = cu_mem_activeids.index(v_focused)
                cu_mem_activeids.delete(idx)
                member.activated = 0
            if EUDElse()():
                # ascending order
                # binary search
                i, epd = EUDCreateVariables(2)
                i << 0
                compc, endc = Forward(), Forward()
                epd = EPD(compc + 4)
                SeqCompute([
                    (epd, SetTo, cu_mem_activeid_contents),
                    (EPD(compc + 8), SetTo, v_focused),
                    (EPD(endc + 8), SetTo, cu_mem_activeids.end)
                ])
                if EUDInfLoop()():
                    EUDBreakIf(endc << MemoryEPD(epd, Exactly, 0))

                    if EUDIf()(compc << Memory(0, AtLeast, 0)):
                        EUDBreak()
                    EUDEndIf()

                    DoActions([
                        i.AddNumber(1),
                        SetMemoryEPD(epd, Add, 1)
                    ])
                EUDEndInfLoop()
                cu_mem_activeids.insert(i, v_focused)
                member.activated = 1
            EUDEndIf()
        EUDEndIf()

    def print(self, writer):
        writer.write_f("\x04CUnit Options, toggle with H (%D / %D)\n",
            v_focused,
            cu_members.length
        )
        quot, mod = f_div(v_focused, 8)
        cur = quot * 8
        pageend = cur + 8
        until = EUDVariable()
        if EUDIf()(pageend <= cu_members.length):
            until << pageend
        if EUDElse()():
            until << cu_members.length
        EUDEndIf()

        # fill contents
        if EUDInfLoop()():
            EUDBreakIf(cur >= until)

            cur_entry = CUnitMemberEntry(cu_members[cur])

            if EUDIf()(cur == v_focused):
                writer.write(0x11) # orange
            if EUDElseIf()(cur_entry.activated == 0):
                writer.write(0x05) # grey
            if EUDElse()():
                writer.write(0x16) # white
            EUDEndIf()

            # 0x***
            offset = cur_entry.off_epd * 4 + cur_entry.off
            q, offd1 = f_div(offset, 16)
            offd3, offd2 = f_div(q, 16)

            for offd in [offd1, offd2, offd3]:
                if EUDIf()(offd <= 9):
                    offd += ord('0')
                if EUDElse()():
                    offd += ord('A') - 10
                EUDEndIf()

            writer.write_f(" +0x%C%C%C %E ",
                offd3,
                offd2,
                offd1,
                cur_entry.name
            )
            comments = cur_entry.comments
            if EUDIfNot()(comments == EPD(0)):
                written = writer.write_strnepd(comments, 10)
                if EUDIf()(written == 10):
                    writer.write_f("...")
                EUDEndIf()
            EUDEndIf()
            writer.write(ord('\n'))

            DoActions([cur.AddNumber(1)])
        EUDEndInfLoop()

        if EUDInfLoop()():
            EUDBreakIf(cur >= pageend)
            writer.write(ord('\n'))
            cur += 1
        EUDEndInfLoop()
        writer.write(0)
