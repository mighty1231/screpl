"""Defines TriggerEditorApp"""

from eudplib import *

from screpl.core.application import Application
from screpl.utils.string import f_memcmp_epd
from screpl.main import get_app_manager
from screpl.main import get_main_writer

app_manager = get_app_manager()
main_writer = get_main_writer()

# trigger with link and without link
# for each type, the trigger is 2408 bytes and 2400 bytes respectively
TYPE_LINK = 0
TYPE_UNLINK = 1

_trig_ptr = EUDVariable()
_trig_epd = EUDVariable()
_trig_type = EUDVariable()

TAB_CONDITION = 0
TAB_ACTION = 1
TAB_END = 2

ENTRY_LINE_LENGTH = 300
ENTRY_COUNT_PER_PAGE = 8

class TriggerEditorApp(Application):
    """Show trigger and modify trigger

    Expected TUI ::

        TrigEditorApp ptr=%H, next=%H
        Conditions:
            ...
        Actions:
            ...
    """

    fields = [
        # trigger related
        'trig_ptr',
        'trig_epd',
        'trig_type',
        'trig_epdsize',
        'cond_epd',
        'act_epd',

        # cache for writing trigger
        'olddb_epd',
        'cond_count',
        'act_count',
        'condtext_table_epd',
        'acttext_table_epd',

        # view related
        'tab',
        'index',
    ]

    @staticmethod
    def set_trig_ptr(trig_ptr, unlink=False):
        """Set initializing variable with pointer

        Args:
            unlink(bool): set trigger type. True for 2400 byte trigger,
                without trigger pointer links. False for 2408 byte trigger,
                with trigger pointer links.
        """
        _trig_ptr << trig_ptr
        _trig_epd << EPD(trig_ptr)
        _trig_type << TYPE_UNLINK if unlink else TYPE_LINK

    @staticmethod
    def set_trig_epd(trig_epd, unlink=False):
        """Set initializing variable with epd

        Args:
            unlink(bool): set trigger type. True for 2400 byte trigger,
                without trigger pointer links. False for 2408 byte trigger,
                with trigger pointer links.
        """
        _trig_ptr << 0x58A364 + 4*trig_epd
        _trig_epd << trig_epd
        _trig_type << TYPE_UNLINK if unlink else TYPE_LINK

    def on_init(self):
        self.trig_ptr = _trig_ptr
        self.trig_epd = _trig_epd
        self.trig_type = _trig_type
        self.trig_epdsize = EUDTernary(_trig_type == TYPE_LINK)(2408//4)(2400//4)

        if EUDIf()(_trig_type == TYPE_LINK):
            self.cond_epd = _trig_epd + 8//4
            self.act_epd = _trig_epd + (8 + 16*20)//4
            self.olddb_epd = app_manager.alloc_db_epd(2408//4)
        if EUDElse()():
            self.cond_epd = _trig_epd
            self.act_epd = _trig_epd + 16*20//4
            self.olddb_epd = app_manager.alloc_db_epd(2400//4)
        EUDEndIf()
        self.cond_count = 0
        self.act_count = 0
        self.condtext_table_epd = app_manager.alloc_db_epd(16*ENTRY_LINE_LENGTH)
        self.acttext_table_epd = app_manager.alloc_db_epd(64*ENTRY_LINE_LENGTH)

        self.tab = TAB_CONDITION
        self.index = 0

        self.update_text()

        _trig_ptr << 0
        _trig_epd << EPD(0)
        _trig_type << TYPE_LINK

    def on_destruct(self):
        app_manager.free_db_epd(self.acttext_table_epd)
        app_manager.free_db_epd(self.condtext_table_epd)
        app_manager.free_db_epd(self.olddb_epd)

    def update_text(self):
        """Update cached text for TUI"""
        condtext_table_epd = self.condtext_table_epd
        acttext_table_epd = self.acttext_table_epd
        cond_epd = self.cond_epd
        act_epd = self.act_epd
        cond_count, act_count = EUDCreateVariables(2)

        # write conditions
        cond_count << 0
        if EUDLoopN()(16):
            # check condtype = 0
            EUDBreakIf(MemoryXEPD(cond_epd + 3, Exactly, 0, 0xFF000000))
            main_writer.seekepd(condtext_table_epd)
            main_writer.write_condition_epd(cond_epd)
            main_writer.write(0)

            DoActions([
                condtext_table_epd.AddNumber(ENTRY_LINE_LENGTH//4),
                cond_epd.AddNumber(20//4),
                cond_count.AddNumber(1),
            ])
        EUDEndLoopN()

        # write actions
        act_count << 0
        if EUDLoopN()(64):
            # check acttype = 0
            EUDBreakIf(MemoryXEPD(act_epd + 6, Exactly, 0, 0xFF0000))
            main_writer.seekepd(acttext_table_epd)
            main_writer.write_action_epd(act_epd)
            main_writer.write(0)

            DoActions([
                acttext_table_epd.AddNumber(ENTRY_LINE_LENGTH//4),
                act_epd.AddNumber(32//4),
                act_count.AddNumber(1),
            ])
        EUDEndLoopN()

        self.cond_count = cond_count
        self.act_count = act_count
        self.index = 0

        # fill old buffer
        f_repmovsd_epd(self.olddb_epd, self.trig_epd, self.trig_epdsize)

        app_manager.request_update()

    def update_index(self, index):
        """Update index with given valid index"""
        tab = self.tab
        if EUDIf()(tab == TAB_CONDITION):
            if EUDIfNot()(index >= self.cond_count):
                self.index = index
                app_manager.request_update()
            EUDEndIf()
        if EUDElse()():
            if EUDIfNot()(index >= self.act_count):
                self.index = index
                app_manager.request_update()
            EUDEndIf()
        EUDEndIf()

    def loop(self):
        if EUDIf()(app_manager.key_press("ESC")):
            app_manager.request_destruct()
            EUDReturn()
        if EUDElseIf()(app_manager.key_press("F7", hold=["LCTRL"])):
            self.update_index(self.index - ENTRY_COUNT_PER_PAGE)
        if EUDElseIf()(app_manager.key_press("F7")):
            self.update_index(self.index - 1)
        if EUDElseIf()(app_manager.key_press("F8", hold=["LCTRL"])):
            self.update_index(self.index + ENTRY_COUNT_PER_PAGE)
        if EUDElseIf()(app_manager.key_press("F8")):
            self.update_index(self.index + 1)
        if EUDElseIf()(app_manager.key_press("R")):
            self.update_text()
        if EUDElseIf()(app_manager.key_press("T", hold=["LCTRL"])):
            tab = self.tab + 1
            if EUDIf()(tab == TAB_END):
                tab << 0
            EUDEndIf()
            self.tab = tab
            self.index = 0
            app_manager.request_update()
        EUDEndIf()
        olddb_epd = self.olddb_epd
        trig_epd = self.trig_epd

        if EUDIfNot()(f_memcmp_epd(olddb_epd, trig_epd, self.trig_epdsize) == 0):
            self.update_text()
        EUDEndIf()

    def print(self, writer):
        trig_ptr = self.trig_ptr
        trig_epd = self.trig_epd
        trig_type = self.trig_type
        tab = self.tab
        index = self.index
        cond_count = self.cond_count
        act_count = self.act_count

        # write header
        EUDSwitch(trig_type)
        if EUDSwitchCase()(TYPE_LINK):
            writer.write_f("Trigger ptr=%H, next=%H\n",
                           trig_ptr, f_dwread_epd(trig_epd + 1))
            EUDBreak()
        if EUDSwitchCase()(TYPE_UNLINK):
            writer.write_f("Trigger ptr=%H, unlinked type\n",
                           trig_ptr)
        EUDEndSwitch()

        # write content
        quot, rem = f_div(index, ENTRY_COUNT_PER_PAGE)
        cur = quot * ENTRY_COUNT_PER_PAGE
        pageend = cur + ENTRY_COUNT_PER_PAGE
        until = EUDVariable()
        text_table_epd = EUDVariable()

        EUDSwitch(tab)
        if EUDSwitchCase()(TAB_CONDITION):
            writer.write_f(" Conditions: (Press CTRL+T to switch)\n")
            text_table_epd << self.condtext_table_epd

            if EUDIf()(pageend <= cond_count):
                until << pageend
            if EUDElse()():
                until << cond_count
            EUDEndIf()
            EUDBreak()
        if EUDSwitchCase()(TAB_ACTION):
            writer.write_f(" Actions:  (Press CTRL+T to switch)\n")
            text_table_epd << self.acttext_table_epd
            if EUDIf()(pageend <= act_count):
                until << pageend
            if EUDElse()():
                until << act_count
            EUDEndIf()
            EUDBreak()
        EUDEndSwitch()

        text_table_epd += cur * (ENTRY_LINE_LENGTH // 4)
        if EUDInfLoop()():
            EUDBreakIf(cur >= until)

            _emp = EUDTernary(cur == index)(0x11)(0x02)
            writer.write_f("%C [%D] %E\n", _emp, cur, text_table_epd)

            DoActions([
                cur.AddNumber(1),
                text_table_epd.AddNumber(ENTRY_LINE_LENGTH // 4),
            ])
        EUDEndInfLoop()

        if EUDInfLoop()():
            EUDBreakIf(cur >= pageend)
            writer.write(ord('\n'))
            cur += 1
        EUDEndInfLoop()

        writer.write(0)
