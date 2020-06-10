from eudplib import *

from screpl.core.application import Application

from . import *
from .cunitrw import cu_members, CUnitMemberEntry

v_focused = EUDVariable()

MODE_MAIN = 0
MODE_HELP = 1
v_mode = EUDVariable()

@EUDFunc
def set_focus(new_focus):
    Trigger(
        conditions=new_focus.AtLeast(0x80000000),
        actions=new_focus.SetNumber(0)
    )
    Trigger(
        conditions=new_focus.AtLeast(cu_members.length),
        actions=new_focus.SetNumber(cu_members.length - 1)
    )
    if EUDIfNot()(v_focused >= cu_members.length):
        v_focused << new_focus
        app_manager.request_update()
    EUDEndIf()

class CUnitOptionApp(Application):
    def on_init(self):
        v_mode << MODE_MAIN

    def loop(self):
        if EUDIf()(app_manager.key_press("ESC")):
            app_manager.request_destruct()
            EUDReturn()
        if EUDElseIf()(app_manager.key_press("F7", hold=["LCTRL"])):
            set_focus(v_focused - 8)
        if EUDElseIf()(app_manager.key_press("F7")):
            set_focus(v_focused - 1)
        if EUDElseIf()(app_manager.key_press("F8", hold=["LCTRL"])):
            set_focus(v_focused + 8)
        if EUDElseIf()(app_manager.key_press("F8")):
            set_focus(v_focused + 1)
        if EUDElseIf()(app_manager.key_press("H")):
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
        if EUDElseIf()(app_manager.key_down("F1")):
            v_mode << MODE_HELP
            app_manager.request_update()
        if EUDElseIf()(app_manager.key_up("F1")):
            v_mode << MODE_MAIN
            app_manager.request_update()
        EUDEndIf()

    def print(self, writer):
        if EUDIf()(v_mode == MODE_MAIN):
            writer.write_f(
                "\x04CUnit Options. press H to toggle entry, "
                "press F1 to get its comment (%D / %D)\n",
                v_focused,
                cu_members.length
            )
            quot = f_div(v_focused, 8)[0]
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

                writer.write_f(" +0x%C%C%C %E ", offd3, offd2, offd1, cur_entry.name_epd)
                comment_epd = cur_entry.comment_epd
                if EUDIfNot()(comment_epd == EPD(0)):
                    written = writer.write_strnepd(comment_epd, 10)
                    if EUDIf()(written == 10):
                        writer.write_f("...")
                    EUDEndIf()
                EUDEndIf()
                writer.write(ord('\n'))

                DoActions([cur.AddNumber(1)])
            EUDEndInfLoop()

        if EUDElse()():
            focused_entry = CUnitMemberEntry(cu_members[v_focused])
            writer.write_f("\x04CUnitMemberEntry \x11%E\x04\n", focused_entry.name_epd)
            focused_comment_epd = focused_entry.comment_epd
            if EUDIfNot()(focused_comment_epd == EPD(0)):
                writer.write_strepd(focused_comment_epd)
            EUDEndIf()
            writer.write(ord("\n"))
        EUDEndIf()
        writer.write(0)
