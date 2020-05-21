from eudplib import *
from repl import (
    Application,
    AppTypedMethod,
    AppCommand,
    argEncNumber,
    print_f
)

from . import *
from .cunitrw import cu_members, CUnitMemberEntry

_cunit_epd = EUDVariable(EPD(0))

def f_epd2ptr(epd):
    return 0x58A364 + (epd * 4)

activemem_size = EUDVariable()

class CUnitDetailApp(Application):
    fields = [
        "cunit_epd",
        "focused_memid"
    ]

    @staticmethod
    def setFocus_epd(cunit_epd):
        _cunit_epd << cunit_epd

    def onInit(self):
        self.focused_memid = 0
        self.cunit_epd = _cunit_epd
        activemem_size << cu_mem_activeids.size
        _cunit_epd << EPD(0)

    def focusMemID(self, new_memid):
        Trigger(
            conditions = new_memid.AtLeast(0x80000000),
            actions = new_memid.SetNumber(0)
        )
        Trigger(
            conditions = new_memid.AtLeast(activemem_size),
            actions = new_memid.SetNumber(activemem_size-1)
        )
        self.focused_memid = new_memid

    def loop(self):
        focused_memid = self.focused_memid
        if EUDIf()(app_manager.keyPress("ESC")):
            app_manager.requestDestruct()
            EUDReturn()
        if EUDElseIf()(app_manager.keyPress("F7", hold=["LCTRL"])):
            self.focusMemID(focused_memid - 8)
        if EUDElseIf()(app_manager.keyPress("F7")):
            self.focusMemID(focused_memid - 1)
        if EUDElseIf()(app_manager.keyPress("F8", hold=["LCTRL"])):
            self.focusMemID(focused_memid + 8)
        if EUDElseIf()(app_manager.keyPress("F8")):
            self.focusMemID(focused_memid + 1)
        if EUDElseIf()(app_manager.keyPress("H", hold=["LCTRL"])):
            dw, epd = f_cunitepdread_epd(EPD(0x6284B8))
            self.cunit_epd = epd
        EUDEndIf()
        app_manager.requestUpdate()

    def print(self, writer):
        cunit_epd = self.cunit_epd
        if EUDIf()(cunit_epd == EPD(0)):
            writer.write_f("\x04CUnit Detail (ptr=NULL) (F7/F8 navigate, CTRL+H selected unit)\n" + "\n"*8)
            writer.write(0)
            EUDReturn()
        EUDEndIf()

        writer.write_f("\x04CUnit Detail (ptr=%H) (F7/F8 navigate, CTRL+H selected unit)\n", f_epd2ptr(cunit_epd))

        focused_memid = self.focused_memid
        quot, mod = f_div(focused_memid, 8)
        cur = quot * 8
        pageend = cur + 8
        until = EUDVariable()
        if EUDIf()(pageend <= activemem_size):
            until << pageend
        if EUDElse()():
            until << activemem_size
        EUDEndIf()

        # fill contents
        if EUDInfLoop()():
            EUDBreakIf(cur >= until)

            if EUDIf()(cur == focused_memid):
                writer.write(0x11) # orange
            if EUDElse()():
                writer.write(0x02) # pale blue
            EUDEndIf()

            cu_member = cu_members[f_dwread_epd(cu_mem_activeid_contents + cur)]
            cu_member = CUnitMemberEntry.cast(cu_member)

            writer.write_f(" %E: ", cu_member.name)
            cu_member.write_f(cunit_epd + cu_member.off_epd, cu_member.off)
            writer.write(ord('\n'))

            DoActions(cur.AddNumber(1))
        EUDEndInfLoop()

        if EUDInfLoop()():
            EUDBreakIf(cur >= pageend)
            writer.write(ord('\n'))
            cur += 1
        EUDEndInfLoop()

        writer.write(0)

    @AppCommand([argEncNumber])
    def p(self, ptr):
        '''
        Set current cunit pointer as ptr
        '''
        label_error = Forward()

        # validity check
        idx, r = f_div(ptr - 0x59CCA8, 336)
        if EUDIfNot()(r == 0):
            EUDJump(label_error)
        EUDEndIf()
        if EUDIf()(idx >= 1700):
            EUDJump(label_error)
        EUDEndIf()

        self.cunit_epd = EPD(ptr)
        EUDReturn()

        label_error << NextTrigger()
        print_f("Warning: ptr %D is not valid CUnit pointer", ptr)
