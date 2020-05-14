from eudplib import *
from repl import (
    Application,
    AppTypedMethod,
    AppCommand,
    argEncNumber
)

from . import *
from .cunitrw import cu_members, Entry

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
        appManager.requestUpdate()
    EUDEndIf()

class CUnitOptionApp(Application):
    def loop(self):
        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
            EUDReturn()
        if EUDElseIf()(appManager.keyPress("F7", hold=["LCTRL"])):
            setFocus(v_focused - 8)
        if EUDElseIf()(appManager.keyPress("F7")):
            setFocus(v_focused - 1)
        if EUDElseIf()(appManager.keyPress("F8", hold=["LCTRL"])):
            setFocus(v_focused + 8)
        if EUDElseIf()(appManager.keyPress("F8")):
            setFocus(v_focused + 1)
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

            cur_entry = Entry(cu_members[cur])

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

            writer.write_f(" +0x%C%C%C %E ",
                offd3+ord('0'),
                offd2+ord('0'),
                offd1+ord('0'),
                cur_entry.name
            )
            if EUDIfNot()(cur_entry.comments == EPD(0)):
                written = writer.write_strnepd(cur_entry.comments, 10)
                if EUDIf()(written == 10):
                    writer.write_f("...")
                EUDEndIf()
            EUDEndIf()
            writer.write("\n")

            DoActions([cur.AddNumber(1)])
        EUDEndInfLoop()

        if EUDInfLoop()():
            EUDBreakIf(cur >= pageend)
            writer.write(ord('\n'))
            cur += 1
        EUDEndInfLoop()
        writer.write(0)
