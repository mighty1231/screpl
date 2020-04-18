from eudplib import *

from ...utils import EUDByteRW, f_raiseError, f_raiseWarning
from ...utils.keycode import getKeyCode
from ..pool import DbPool, VarPool

_manager = None

def getAppManager(superuser=None):
    global _manager
    if superuser is None:
        assert _manager is not None
    else:
        assert _manager is None
        _manager = AppManager(superuser)
    return _manager

class AppManager:
    _APP_MAX_COUNT_ = 30
    def __init__(self, superuser):
        from . import ApplicationInstance

        self.superuser = EncodePlayer(superuser)
        assert 0 <= self.superuser < 8, "Superuser should be one of P1 ~ P8"

        self.update = EUDVariable(initval=0)
        self.destruct = EUDVariable(initval=0)

        self.writer = EUDByteRW()
        self.displayBuffer = DBString(5000)

        self.dbpool = DbPool(300000)
        self.varpool = VarPool(800)

        self.current_app_instance = ApplicationInstance(self)

        self.app_cnt = EUDVariable(0)
        self.app_method_stack = EUDArray(AppManager._APP_MAX_COUNT_)
        self.app_cmdtab_stack = EUDArray(AppManager._APP_MAX_COUNT_)
        self.app_member_stack = EUDArray(AppManager._APP_MAX_COUNT_)

        if EUDExecuteOnce()():
            self.cur_methods = EUDVArray(12345)(_from=EUDVariable())
            self.cur_members = EUDVArray(12345)(_from=EUDVariable())
        EUDEndExecuteOnce()
        self.cur_cmdtable_epd = EUDVariable()

        self.keystates = EPD(Db(0x100 * 4))
        self.keystates_sub = EPD(Db(0x100 * 4))

    def allocVariable(self, count):
        return self.varpool.alloc(count)

    def freeVariable(self, ptr):
        self.varpool.free(ptr)

    def allocDb_epd(self, sizequarter):
        ''' allocate SIZEQUARTER*4 bytes '''
        return self.dbpool.alloc_epd(sizequarter)

    def freeDb_epd(self, epd):
        self.dbpool.free_epd(epd)

    def getCurrentAppInstance(self):
        return self.current_app_instance

    def openApplication(self, app):
        from . import Application

        app.allocate()

        # @TODO decide the moment when new app emerges
        assert issubclass(app, Application)
        if EUDIf()(self.app_cnt < AppManager._APP_MAX_COUNT_):
            members = self.allocVariable(len(app._fields_))
            self.cur_members      << members
            self.cur_members._epd << EPD(members)
            self.cur_methods      << app._methodarray_
            self.cur_methods._epd << app._methodarray_epd_
            self.cur_cmdtable_epd << EPD(app._cmdtable_)

            self.app_member_stack[self.app_cnt] = members
            self.app_method_stack[self.app_cnt] = app._methodarray_
            self.app_cmdtab_stack[self.app_cnt] = EPD(app._cmdtable_)
            self.app_cnt += 1

            self.current_app_instance.cmd_output_epd = 0
            self.current_app_instance.init()
            self.requestUpdate()
        if EUDElse()():
            f_raiseWarning("APP COUNT reached MAX, No more spaces")
        EUDEndIf()

    def terminateApplication(self):
        if EUDIf()(self.app_cnt == 1):
            f_raiseError("FATAL ERROR: Excessive TerminateApplication")
        EUDEndIf()

        self.current_app_instance.destruct()
        self.freeVariable(self.cur_members)

        self.app_cnt -= 1
        members   = self.app_member_stack[self.app_cnt]
        methods   = self.app_method_stack[self.app_cnt]
        table_epd = self.app_cmdtab_stack[self.app_cnt]

        self.cur_members      << members
        self.cur_members._epd << EPD(members)
        self.cur_methods      << methods
        self.cur_methods._epd << EPD(methods)
        self.cur_cmdtable_epd << table_epd

    def updateKeyState(self):
        # keystate
        # 0: not changed
        # 1, 2, ..., n: key down with consecutive n frames
        # -1: key up
        prev_states = EPD(Db(0x100))

        prevs = [Forward() for _ in range(4*4)]
        curs = [Forward() for _ in range(4*4)]
        states_cond = [Forward() for _ in range(4)]
        states = [Forward() for _ in range(4*4)]
        subs = [Forward() for _ in range(3*4)]

        actions = [SetMemory(prev + 4, SetTo, prev_states) for prev in prevs]
        actions += [SetMemory(cur + 4, SetTo, EPD(0x596A18)) for cur in curs]
        actions += [SetMemory(state + 4, SetTo, self.keystates + i)
                    for i, state in enumerate(states_cond)]
        actions += [SetMemory(state + 16, SetTo, self.keystates + i//4)
                    for i, state in enumerate(states)]
        actions += [SetMemory(sub + 16, SetTo, self.keystates_sub + i//3)
                    for i, sub in enumerate(subs)]
        DoActions(actions)

        if EUDLoopN()(0x100 // 4):
            for i, pos in enumerate([1, 0x100, 0x10000, 0x1000000]):
                # 0->0: set 0
                Trigger(
                    conditions = [
                        prevs[4*i] << MemoryX(0, Exactly, 0, 0xFF * pos),
                        curs[4*i] << MemoryX(0, Exactly, 0, 0xFF * pos)
                    ],
                    actions = [
                        states[4*i] << SetMemory(0x58A364, SetTo, 0)
                    ]
                )
                # 0->1: set 1
                Trigger(
                    conditions = [
                        prevs[4*i+1] << MemoryX(0, Exactly, 0, 0xFF * pos),
                        curs[4*i+1] << MemoryX(0, Exactly, pos, 0xFF * pos)
                    ],
                    actions = [
                        states[4*i+1] << SetMemory(0, SetTo, 1),
                        subs[3*i] << SetMemory(0, SetTo, 1),
                    ]
                )
                # 1->0: set -1
                Trigger(
                    conditions = [
                        prevs[4*i+2] << MemoryX(0, Exactly, pos, 0xFF * pos),
                        curs[4*i+2] << MemoryX(0, Exactly, 0, 0xFF * pos)
                    ],
                    actions = [states[4*i+2] << SetMemory(0, SetTo, 2**32-1)]
                )
                # 1->1: +1
                Trigger(
                    conditions = [
                        prevs[4*i+3] << MemoryX(0, Exactly, pos, 0xFF * pos),
                        curs[4*i+3] << MemoryX(0, Exactly, pos, 0xFF * pos)
                    ],
                    actions = [
                        states[4*i+3] << SetMemory(0, Add, 1),
                        subs[3*i+1] << SetMemory(0, SetTo, 0),
                    ]
                )
                # subs (consecutive keydown)
                Trigger(
                    conditions = [
                        states_cond[i] << Memory(0, AtLeast, 5)
                    ],
                    actions = [
                        subs[3*i+2] << SetMemory(0, SetTo, 1)
                    ]
                )

            actions = [SetMemory(prev + 4, Add, 1) for prev in prevs]
            actions += [SetMemory(cur + 4, Add, 1) for cur in curs]
            actions += [SetMemory(state + 4, Add, 4) for state in states_cond]
            actions += [SetMemory(state + 16, Add, 4) for state in states]
            actions += [SetMemory(sub + 16, Add, 4) for sub in subs]
            DoActions(actions)
        EUDEndLoopN()
        f_repmovsd_epd(prev_states, EPD(0x596A18), 0x100//4)

    def keyDown(self, key):
        # Example. shift + f7
        # if EUDIf()([manager.keyDown(0xA0), manager.keyDown(0x76))]):
        #     event()
        # EUDEndIf()
        key = getKeyCode(key)
        return MemoryEPD(self.keystates + key, Exactly, 1)

    def keyUp(self, key):
        key = getKeyCode(key)
        return MemoryEPD(self.keystates + key, Exactly, 2**32-1)

    def keyPress(self, key):
        key = getKeyCode(key)
        return [MemoryEPD(self.keystates + key, Exactly, 1),
            MemoryEPD(self.keystates_sub + key, Exactly, 1)]

    def requestUpdate(self):
        '''
        Request update of application
        Should be called under AppMethod or AppCommand
        '''
        self.update << 1

    def requestDestruct(self):
        '''
        Request self-destruct of application
        Should be called under AppMethod or AppCommand
        '''
        self.destruct << 1

    def getWriter(self):
        '''
        Internally printing function uses this method
        '''
        return self.writer

    def loop(self):
        from ...app.repl import REPL
        if EUDExecuteOnce()():
            self.openApplication(REPL)
        EUDEndExecuteOnce()

        self.updateKeyState()

        # process all new chats
        prev_txtPtr = EUDVariable(initval=10)
        after_chat = Forward()
        if EUDIf()(Memory(0x640B58, Exactly, prev_txtPtr)):
            EUDJump(after_chat)
        EUDEndIf()

        # copy superuser name
        prefix = Db(36)
        f_strcpy(prefix, 0x57EEEB + 36*self.superuser)
        prefixlen = f_strlen(0x57EEEB + 36*self.superuser)

        cur_txtPtr = f_dwread_epd(EPD(0x640B58))
        i = EUDVariable()
        i << prev_txtPtr
        chat_off = 0x640B60 + 218 * i

        if EUDInfLoop()():
            EUDBreakIf(i == cur_txtPtr)
            if EUDIf()(f_memcmp(chat_off, prefix, prefixlen) == 0):
                # 3 = colorcode, colon, spacebar
                new_chat_off = chat_off + (prefixlen + 3)

                # run AppCommand on foreground app
                self.current_app_instance.chatCallback(new_chat_off)
            EUDEndIf()
            if EUDIf()(i == 10):
                i << 0
                chat_off << 0x640B60
            if EUDElse()():
                i += 1
                chat_off += 218
            EUDEndIf()
        EUDEndInfLoop()
        prev_txtPtr << cur_txtPtr

        after_chat << NextTrigger()

        # loop
        self.current_app_instance.loop()

        # check destruction
        if EUDIf()(self.destruct == 1):
            self.terminateApplication()
            self.current_app_instance.loop()

            self.destruct << 0
            self.update << 1
        EUDEndIf()

        # Print top of the screen, enables chat simultaneously
        txtPtr = f_dwread_epd(EPD(0x640B58))
        if EUDIf()(self.update == 1):
            self.writer.seekepd(EPD(self.displayBuffer.GetStringMemoryAddr()))

            # print() uses self.writer internally
            self.current_app_instance.print()

            self.update << 0
        EUDEndIf()
        f_setcurpl(self.superuser)
        self.displayBuffer.Display()
        SeqCompute([(EPD(0x640B58), SetTo, txtPtr)])
