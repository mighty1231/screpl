from eudplib import *

from ..base.eudbyterw import EUDByteRW
from ..base.pool import DbPool, VarPool
from ..utils import f_raiseError, f_raiseWarning, getKeyCode, f_strlen
from .bridge import bridge_init, bridge_loop

KEYPRESS_DELAY = 8
_manager = None

BRIDGE_OFF = 0
BRIDGE_ON = 1
BRIDGE_BLIND = 2

trigger_framedelay = EUDVariable(-1)

def getAppManager():
    global _manager
    assert _manager

    return _manager

class AppManager:
    _APP_MAX_COUNT_ = 30

    @staticmethod
    def initialize(*args, **kwargs):
        global _manager
        assert _manager is None
        _manager = AppManager(*args, **kwargs)

    def __init__(self, superuser, superuser_mode, bridge_mode):
        from .application import ApplicationInstance

        # set superuser
        modes = ["playerNumber", "playerID"]
        if superuser_mode == modes[0]:

            # evaluate chat prefix by player number
            self.superuser = EncodePlayer(playerMap.get(superuser, superuser))
            assert 0 <= self.superuser < 8, "Superuser should be one of P1 ~ P8"
            print("[SC-REPL] Given superuser playerNumber = %d" % self.superuser)

            # copy superuser name
            self.su_prefix = Db(36)
            su_writer = EUDByteRW()
            su_writer.seekepd(EPD(self.su_prefix))
            su_writer.write_str(0x57EEEB + 36*self.superuser)
            su_writer.write(58) # colon
            su_writer.write(7)  # color code
            su_writer.write(32) # space
            su_writer.write(0)

            self.su_prefixlen = f_strlen(self.su_prefix)
        elif superuser_mode == modes[1]:

            # evaluate player number and chat prefix by player name
            print("[SC-REPL] Given superuser playerID = '%s'" % superuser)

            self.su_prefix = Db(u2b(superuser) + bytes([58, 7, 32, 0]))
            self.su_prefixlen = len(superuser)+3
            self.superuser = EUDVariable(0)

            name_ptr = EUDVariable(0x57EEEB)
            if EUDWhile()(name_ptr <= 0x57EEEB + 36*7):
                if EUDIf()(f_strcmp(name_ptr, Db(u2b(superuser) + b'\0')) == 0):
                    EUDBreak()
                EUDEndIf()
                DoActions([
                    name_ptr.AddNumber(36),
                    self.superuser.AddNumber(1)
                ])
            EUDEndWhile()
            if EUDIf()(self.superuser == 8):
                f_raiseError("[SC-REPL] superuser '%s' not found" % superuser)
            EUDEndIf()
        else:
            raise RuntimeError("Unknown superuser mode, please set among {}"
                    .format(modes))

        # pool supports for application instances
        self.dbpool = DbPool(300000)
        self.varpool = VarPool(800)

        # variables that support several apps
        self.current_app_instance = ApplicationInstance()
        self.app_cnt = EUDVariable(0)
        self.cur_app_id = EUDVariable(-1)
        self.app_method_stack = EUDArray(AppManager._APP_MAX_COUNT_)
        self.app_cmdtab_stack = EUDArray(AppManager._APP_MAX_COUNT_)
        self.app_member_stack = EUDArray(AppManager._APP_MAX_COUNT_)
        if EUDExecuteOnce()():
            self.cur_methods = EUDVArray(12345)(_from=EUDVariable())
            self.cur_members = EUDVArray(12345)(_from=EUDVariable())
        EUDEndExecuteOnce()

        # related to life cycle of app
        self.is_starting_app = EUDVariable(0)
        self.is_terminating_app = EUDVariable(0)

        # text ui
        self.writer = EUDByteRW()
        self.displayBuffer = DBString(5000)
        self.update = EUDVariable(initval=0)
        self.cur_cmdtable_epd = EUDVariable()

        # common useful value that app may use
        self.keystates = EPD(Db(0x100 * 4))
        self.keystates_sub = EPD(Db(0x100 * 4))
        self.mouse_prev_state = EUDVariable(0)
        self.mouse_state = EUDArray([1, 1, 1])
        self.mouse_pos = EUDCreateVariables(2)
        self.current_frame_number = EUDVariable(0)

        # 64, 96, 128, 192, 256
        # Multiply 32 to get pixel coordinate
        dim = GetChkTokenized().getsection(b'DIM ')
        self.mapWidth = b2i2(dim, 0)
        self.mapHeight = b2i2(dim, 2)

        # bridge_mode
        bridge_mode = bridge_mode.lower()
        if bridge_mode == 'on':
            self.bridge_mode = BRIDGE_ON
            bridge_init()
            self.is_blind_mode = EUDVariable(0)
        elif bridge_mode == 'blind':
            self.bridge_mode = BRIDGE_BLIND
            bridge_init()
            self.is_blind_mode = EUDVariable(1)
        elif bridge_mode == 'off':
            self.bridge_mode = BRIDGE_OFF
        else:
            raise RuntimeError("Unknown 'bridge_mode' = '%s', "\
                    "expected 'on', 'off', or 'blind'" % bridge_mode)

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

    def startApplication(self, app):
        '''
        It just reserve to start app.
        The app is initialized at the start of the next loop.
        '''
        from .application import Application
        assert issubclass(app, Application)

        app.allocate()
        self._startApplication(len(app._fields_), app._methodarray_, EPD(app._cmdtable_))

    @EUDMethod
    def _startApplication(self, fieldsize, methods, table_epd):
        if EUDIfNot()(self.is_terminating_app == 0):
            f_raiseError("FATAL ERROR: startApplication <-> requestDestruct")
        EUDEndIf()

        if EUDIf()(self.app_cnt < AppManager._APP_MAX_COUNT_):
            self.app_member_stack[self.app_cnt] = self.allocVariable(fieldsize)
            self.app_method_stack[self.app_cnt] = methods
            self.app_cmdtab_stack[self.app_cnt] = table_epd
            self.app_cnt += 1

            self.is_starting_app << 1
        if EUDElse()():
            f_raiseWarning("APP COUNT reached MAX, No more spaces")
        EUDEndIf()

    def initOrTerminateApplication(self):
        # Terminate one
        if EUDIfNot()(self.is_terminating_app == 0):
            if EUDIf()(self.app_cnt == 1):
                f_raiseError("FATAL ERROR: Excessive TerminateApplication")
            EUDEndIf()

            self.current_app_instance.onDestruct()
            self.freeVariable(self.cur_members)

            self.app_cnt -= 1
            self.cur_app_id << self.app_cnt - 1
            members    = self.app_member_stack[self.cur_app_id]
            methods    = self.app_method_stack[self.cur_app_id]
            table_epd  = self.app_cmdtab_stack[self.cur_app_id]

            self.cur_members      << members
            self.cur_members._epd << EPD(members)
            self.cur_methods      << methods
            self.cur_methods._epd << EPD(methods)
            self.cur_cmdtable_epd << table_epd

            self.current_app_instance.onResume()

            self.is_terminating_app << 0
        EUDEndIf()

        # Initialize one or more
        if EUDIfNot()(self.is_starting_app == 0):
            if EUDInfLoop()():
                self.cur_app_id += 1
                members    = self.app_member_stack[self.cur_app_id]
                methods    = self.app_method_stack[self.cur_app_id]
                table_epd  = self.app_cmdtab_stack[self.cur_app_id]

                self.cur_members      << members
                self.cur_members._epd << EPD(members)
                self.cur_methods      << methods
                self.cur_methods._epd << EPD(methods)
                self.cur_cmdtable_epd << table_epd

                self.current_app_instance.cmd_output_epd = 0
                self.current_app_instance.onInit()

                EUDBreakIf(self.cur_app_id >= self.app_cnt - 1)
            EUDEndInfLoop()

            self.is_starting_app << 0
        EUDEndIf()

        self.cleanText()
        self.requestUpdate()

    def updateKeyState(self):
        # keystate
        # 0: not changed
        # 1, 2, ..., n: key down with consecutive n frames
        # -1: key up
        prev_states = EPD(Db(0x100))

        prevs = [Forward() for _ in range(4*4)]
        curs = [Forward() for _ in range(4*4)]
        states_cond = [Forward() for _ in range(2*4)]
        states = [Forward() for _ in range(4*4)]
        subs = [Forward() for _ in range(4*4)]

        actions = [SetMemory(prev + 4, SetTo, prev_states) for prev in prevs]
        actions += [SetMemory(cur + 4, SetTo, EPD(0x596A18)) for cur in curs]
        actions += [SetMemory(state + 4, SetTo, self.keystates + i//2)
                    for i, state in enumerate(states_cond)]
        actions += [SetMemory(state + 16, SetTo, self.keystates + i//4)
                    for i, state in enumerate(states)]
        actions += [SetMemory(sub + 16, SetTo, self.keystates_sub + i//4)
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
                        subs[4*i] << SetMemory(0, SetTo, 1),
                    ]
                )
                # 1->0: set -1
                Trigger(
                    conditions = [
                        prevs[4*i+2] << MemoryX(0, Exactly, pos, 0xFF * pos),
                        curs[4*i+2] << MemoryX(0, Exactly, 0, 0xFF * pos)
                    ],
                    actions = [
                        states[4*i+2] << SetMemory(0, SetTo, 2**32-1),
                        subs[4*i+1] << SetMemory(0, SetTo, 0),
                    ]
                )
                # 1->1: +1
                Trigger(
                    conditions = [
                        prevs[4*i+3] << MemoryX(0, Exactly, pos, 0xFF * pos),
                        curs[4*i+3] << MemoryX(0, Exactly, pos, 0xFF * pos)
                    ],
                    actions = [
                        states[4*i+3] << SetMemory(0, Add, 1),
                        subs[4*i+2] << SetMemory(0, SetTo, 0),
                    ]
                )
                # subs (consecutive keydown)
                Trigger(
                    conditions = [
                        states_cond[2*i] << Memory(0, AtLeast, KEYPRESS_DELAY),
                        states_cond[2*i+1] << Memory(0, AtMost, 2**31-1)
                    ],
                    actions = [
                        subs[4*i+3] << SetMemory(0, SetTo, 1)
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
        key = getKeyCode(key)
        return MemoryEPD(self.keystates + key, Exactly, 1)

    def keyUp(self, key):
        key = getKeyCode(key)
        return MemoryEPD(self.keystates + key, Exactly, 2**32-1)

    def keyPress(self, key, hold=[]):
        '''
        hold: list of keys, such as LCTRL, LSHIFT, LALT, etc...
        '''
        key = getKeyCode(key)
        actions = [MemoryEPD(self.keystates + key, AtLeast, 1),
            MemoryEPD(self.keystates_sub + key, Exactly, 1)]
        for holdkey in hold:
            holdkey = getKeyCode(holdkey)
            actions.append(MemoryEPD(self.keystates + holdkey, AtLeast, 1))
        return actions

    @EUDMethod
    def getCurrentFrameNumber(self):
        '''
        Counter that measures how much loops are called
        '''
        return self.current_frame_number

    def updateMouseState(self):
        # up   -> up   : 1
        # up   -> down : 2
        # down -> up   : 0
        # down -> down : 3
        for i, c in enumerate([2, 8, 32]): # L, R, M
            for _bef, _cur, _state in [(0, 0, 1), (0, 1, 2), (1, 0, 0), (1, 1, 3)]:
                Trigger(
                    conditions = [
                        self.mouse_prev_state.ExactlyX(c * _bef, c),
                        MemoryX(0x6CDDC0, Exactly, c * _cur, c)
                    ], actions = SetMemoryEPD(EPD(self.mouse_state) + i, SetTo, _state)
                )
            # store previous value
            Trigger(
                conditions=MemoryX(0x6CDDC0, Exactly, c, c),
                actions=self.mouse_prev_state.SetNumberX(c, c)
            )
            Trigger(
                conditions=MemoryX(0x6CDDC0, Exactly, 0, c),
                actions=self.mouse_prev_state.SetNumberX(0, c)
            )

        # mouse position
        x, y = self.mouse_pos
        x << f_dwread_epd(EPD(0x0062848C)) + f_dwread_epd(EPD(0x006CDDC4))
        y << f_dwread_epd(EPD(0x006284A8)) + f_dwread_epd(EPD(0x006CDDC8))

    def mouseLClick(self):
        return MemoryEPD(EPD(self.mouse_state), Exactly, 0)

    def mouseLPress(self):
        return MemoryEPD(EPD(self.mouse_state), AtLeast, 2)

    def mouseRClick(self):
        return MemoryEPD(EPD(self.mouse_state+1), Exactly, 0)

    def mouseRPress(self):
        return MemoryEPD(EPD(self.mouse_state+1), AtLeast, 2)

    def mouseMClick(self):
        return MemoryEPD(EPD(self.mouse_state+2), Exactly, 0)

    def mouseMPress(self):
        return MemoryEPD(EPD(self.mouse_state+2), AtLeast, 2)

    @EUDMethod
    def getMousePositionXY(self):
        x, y = self.mouse_pos
        EUDReturn([x, y])

    def getMapWidth(self):
        # 64, 96, 128, 192, 256
        # Multiply 32 to get pixel coordinate
        return self.mapWidth

    def getMapHeight(self):
        # 64, 96, 128, 192, 256
        # Multiply 32 to get pixel coordinate
        return self.mapHeight


    def requestUpdate(self):
        '''
        Request update of application
        Should be called under AppMethod or AppCommand
        '''
        self.update << 1

    def requestDestruct(self):
        '''
        Request self-destruct of application
        It should be called under AppMethod or AppCommand

        When a single app requested startApplication,
          destruction should not be requested at the same frame.
        '''
        if EUDIfNot()(self.is_starting_app == 0):
            f_raiseError("FATAL ERROR: startApplication <-> requestDestruct")
        EUDEndIf()
        self.is_terminating_app << 1

    def setTriggerDelay(self, delay):
        trigger_framedelay << delay

    def unsetTriggerDelay(self):
        trigger_framedelay << -1

    def cleanText(self):
        # clean text UI of previous app
        if self.bridge_mode:
            EUDIf()(self.is_blind_mode == 0)

        f_setcurpl(self.superuser)
        DoActions(DisplayText("\n" * 12))

        if self.bridge_mode:
            EUDEndIf()

    def getWriter(self):
        '''
        Internally printing function uses this method
        '''
        return self.writer

    def loop(self):
        from ..apps.repl import REPL
        from .appcommand import AppCommand

        # bridge command
        if self.bridge_mode:
            @AppCommand([])
            def toggleBlind(repl):
                self.is_blind_mode << 1 - self.is_blind_mode
            REPL.addCommand("blind", toggleBlind)

        if EUDExecuteOnce()():
            self.startApplication(REPL)
        EUDEndExecuteOnce()

        self.updateMouseState()
        self.updateKeyState()

        # turbo mode
        if EUDIfNot()(trigger_framedelay.Exactly(-1)):
            DoActions(SetMemory(0x6509A0, SetTo, trigger_framedelay))
        EUDEndIf()

        if EUDIfNot()([self.is_terminating_app == 0, self.is_starting_app == 0]):
            self.initOrTerminateApplication()
        EUDEndIf()

        # process all new chats
        prev_txtPtr = EUDVariable(initval=10)
        after_chat = Forward()
        if EUDIf()(Memory(0x640B58, Exactly, prev_txtPtr)):
            EUDJump(after_chat)
        EUDEndIf()

        # parse updated lines
        cur_txtPtr = f_dwread_epd(EPD(0x640B58))
        i = EUDVariable()
        i << prev_txtPtr
        chat_off = 0x640B60 + 218 * i
        if EUDInfLoop()():
            EUDBreakIf(i == cur_txtPtr)
            if EUDIf()(f_memcmp(chat_off, self.su_prefix, self.su_prefixlen) == 0):
                self.current_app_instance.onChat(chat_off + self.su_prefixlen)
            EUDEndIf()

            # search next updated lines
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

        # print top of the screen, enables chat simultaneously
        # option - blind mode
        #    1. save gametext
        #    2. print text ui
        #    3. send displayed text to bridge
        #    4. restore gametext
        txtPtr = f_dwread_epd(EPD(0x640B58))
        if self.bridge_mode:
            previous_gameText = Db(11*218 + 2)

        if EUDIfNot()(self.update == 0):
            self.writer.seekepd(EPD(self.displayBuffer.GetStringMemoryAddr()))

            # print() uses self.writer internally
            self.current_app_instance.print()

            self.update << 0
        EUDEndIf()
        f_setcurpl(self.superuser)

        if self.bridge_mode:
            if EUDIf()(self.is_blind_mode == 1):
                f_repmovsd_epd(EPD(previous_gameText), EPD(0x640B60), (11*218+2) // 4)
            EUDEndIf()

        self.displayBuffer.Display()
        SeqCompute([(EPD(0x640B58), SetTo, txtPtr)])

        self.current_frame_number += 1
        if self.bridge_mode:
            bridge_loop(self)
            if EUDIf()(self.is_blind_mode == 1):
                f_repmovsd_epd(EPD(0x640B60), EPD(previous_gameText), (11*218+2) // 4)
            EUDEndIf()


playerMap = {
    'P1':P1,
    'P2':P2,
    'P3':P3,
    'P4':P4,
    'P5':P5,
    'P6':P6,
    'P7':P7,
    'P8':P8,
    'Player1':Player1,
    'Player2':Player2,
    'Player3':Player3,
    'Player4':Player4,
    'Player5':Player5,
    'Player6':Player6,
    'Player7':Player7,
    'Player8':Player8,
}
