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

        self.current_app_instance = ApplicationInstance()

        self.app_cnt = EUDVariable(0)
        self.app_method_stack = EUDArray(AppManager._APP_MAX_COUNT_)
        self.app_member_stack = EUDArray(AppManager._APP_MAX_COUNT_)
        self.app_cmdtable_stack = EUDArray(AppManager._APP_MAX_COUNT_)

        self.current_app_cmdtable_epd = EUDVariable()

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

        app.initialize()

        # @TODO decide the moment when new app emerges
        assert issubclass(app, Application)
        if EUDIf()(self.app_cnt < AppManager._APP_MAX_COUNT_):
            self.current_app_instance._methodptr << app._methodarray_
            self.current_app_instance._memberptr << self.allocVariable(len(app._fields_) + 1)
            self.current_app_instance._cmdtable_epd << EPD(app._cmdtable_)
            self.current_app_instance._update()
            self.current_app_instance.cmd_output_epd = 0

            self.app_method_stack[self.app_cnt] = self.current_app_instance._methodptr
            self.app_member_stack[self.app_cnt] = self.current_app_instance._memberptr
            self.app_cmdtable_stack[self.app_cnt] = self.current_app_instance._cmdtable_epd

            self.app_cnt += 1

            self.current_app_instance.init()
            self.requestUpdate()
        if EUDElse()():
            f_raiseWarning("APP COUNT reached MAX, No more spaces")
        EUDEndIf()

    def shutApplication(self):
        if EUDIf()(self.app_cnt == 0):
            f_raiseError("FATAL ERROR: Application shutdown")
        EUDEndIf()
        self.current_app_instance.destruct()

        self.app_cnt -= 1
        self.freeVariable(self.current_app_instance._memberptr)
        self.current_app_instance._methodptr << self.app_method_stack[self.app_cnt]
        self.current_app_instance._memberptr << self.app_member_stack[self.app_cnt]
        self.current_app_instance._cmdtable_epd << self.app_cmdtable_stack[self.app_cnt]
        self.current_app_instance._update()

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

        prefix = Db(36)
        f_strcpy(prefix, 0x57EEEB + 36*self.superuser)
        prefixlen = f_strlen(0x57EEEB + 36*self.superuser)

        # process all new chats
        prev_txtPtr = EUDVariable(initval=10)
        i = EUDVariable()
        cur_txtPtr = f_dwread_epd(EPD(0x640B58))
        chat_off = 0x640B60 + 218 * prev_txtPtr

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

        # loop
        self.current_app_instance.loop()

        # check destruction
        if EUDIf()(self.destruct == 1):
            self.shutApplication()
            self.current_app_instance.loop()

            self.destruct << 0
            self.update << 1
        EUDEndIf()

        # update display
        if EUDIf()(self.update == 1):
            # Print top of the screen, you can chat at the same time
            txtPtr = f_dwread_epd(EPD(0x640B58))

            f_setcurpl(self.superuser)

            self.writer.seekepd(EPD(self.displayBuffer.GetStringMemoryAddr()))
            self.current_app_instance.print() # it uses self.writer
            self.displayBuffer.Display()

            SeqCompute([(EPD(0x640B58), SetTo, txtPtr)])
            self.update << 0
        EUDEndIf()
