from eudplib import *
from repl import (
    Application,
    AppTypedMethod,
    AppCommand,
    argEncNumber
)

from . import *
from .cunitrw import cu_members, CUnitMemberEntry

_cunit_epd = EUDVariable(EPD(0))

def f_epd2ptr(epd):
    return 0x58A364 + (epd * 4)

activemem_size = EUDVariable()
activemem_contents = EUDVariable()

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
        activemem_contents << cu_mem_activeids.contents
        _cunit_epd << EPD(0)

    def loop(self):
        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
            EUDReturn()
        EUDEndIf()
        appManager.requestUpdate()

    def print(self, writer):
        cunit_epd = self.cunit_epd
        writer.write_f("\x04CUnit Detail (ptr=%H)\n", f_epd2ptr(cunit_epd))

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

            cu_member = cu_members[f_dwread_epd(activemem_contents + cur)]
            cu_member = CUnitMemberEntry.cast(cu_member)

            writer.write_f(" %E= ", cu_member.name)
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
