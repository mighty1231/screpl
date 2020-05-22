from eudplib import *

from repl.utils.eudbyterw import EUDByteRW
from repl.utils.pool import DbPool, VarPool
from repl.utils.debug import f_raise_error, f_raise_warning, f_printf
from repl.utils.keycode import getKeyCode
from repl.utils.string import f_strlen

import repl.main as main

_KEYPRESS_DELAY = 8
_APP_MAX_COUNT = 30

class PayloadSizeObj(EUDObject):
    def GetDataSize(self):
        return 4

    def CollectDependency(self, emitbuffer):
        pass

    def WritePayload(self, emitbuffer):
        from eudplib.core.allocator.payload import _payload_size
        emitbuffer.WriteDword(_payload_size)

class AppManager:
    def __init__(self, su_id, su_prefix, su_prefixlen):
        from .application import ApplicationInstance

        self.su_id = su_id
        self.su_prefix = su_prefix
        self.su_prefixlen = su_prefixlen

        # pool supports for application instances
        self.dbpool = DbPool(300000)
        self.varpool = VarPool(800)

        # variables that support several apps
        self.current_app_instance = ApplicationInstance()
        self.app_cnt = EUDVariable(0)
        self.cur_app_id = EUDVariable(-1)
        self.app_method_stack = EUDArray(_APP_MAX_COUNT)
        self.app_cmdtab_stack = EUDArray(_APP_MAX_COUNT)
        self.app_member_stack = EUDArray(_APP_MAX_COUNT)
        if EUDExecuteOnce()():
            self.cur_methods = EUDVArray(12345)(_from=EUDVariable())
            self.cur_members = EUDVArray(12345)(_from=EUDVariable())
        EUDEndExecuteOnce()
        self.cur_cmdtable_epd = EUDVariable()

        # related to life cycle of app
        self.is_starting_app = EUDVariable(0)
        self.is_terminating_app = EUDVariable(0)

        # text ui
        self.display_buffer = Db(4000)
        self.update = EUDVariable(initval=0)

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
        self.map_width = b2i2(dim, 0)
        self.map_height = b2i2(dim, 2)
        self.payload_size = f_dwread_epd(EPD(PayloadSizeObj()))

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
            f_raise_error("FATAL ERROR: startApplication <-> requestDestruct")
        EUDEndIf()

        if EUDIf()(self.app_cnt < _APP_MAX_COUNT):
            self.app_member_stack[self.app_cnt] = self.allocVariable(fieldsize)
            self.app_method_stack[self.app_cnt] = methods
            self.app_cmdtab_stack[self.app_cnt] = table_epd
            self.app_cnt += 1

            self.is_starting_app << 1
        if EUDElse()():
            f_raise_warning("APP COUNT reached MAX, No more spaces")
        EUDEndIf()

    def initOrTerminateApplication(self):
        # Terminate one
        if EUDIfNot()(self.is_terminating_app == 0):
            if EUDIf()(self.app_cnt == 1):
                f_raise_error("FATAL ERROR: Excessive TerminateApplication")
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

        self.clean_text()
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
                        states_cond[2*i] << Memory(0, AtLeast, _KEYPRESS_DELAY),
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
        ret = [
            Memory(0x68C144, Exactly, 0),               # chat status - not chatting
            MemoryEPD(self.keystates + key, Exactly, 1)
        ]
        return ret

    def keyUp(self, key):
        key = getKeyCode(key)
        ret = [
            Memory(0x68C144, Exactly, 0),               # chat status - not chatting
            MemoryEPD(self.keystates + key, Exactly, 2**32-1)
        ]
        return ret

    def keyPress(self, key, hold=[]):
        '''
        hold: list of keys, such as LCTRL, LSHIFT, LALT, etc...
        '''
        key = getKeyCode(key)
        actions = [
            Memory(0x68C144, Exactly, 0),               # chat status - not chatting
            MemoryEPD(self.keystates + key, AtLeast, 1),
            MemoryEPD(self.keystates_sub + key, Exactly, 1)
        ]
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
        return self.map_width

    def getMapHeight(self):
        # 64, 96, 128, 192, 256
        # Multiply 32 to get pixel coordinate
        return self.map_height

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
            f_raise_error("FATAL ERROR: startApplication <-> requestDestruct")
        EUDEndIf()
        self.is_terminating_app << 1

    @EUDMethod
    def exportAppOutputToBridge(self, src_buffer, size):
        from repl.bridge_server.blocks.appoutput import (
            APP_OUTPUT_MAXSIZE,
            appOutputSize,
            appOutputBuffer,
        )
        from repl.main import is_bridge_mode

        if not is_bridge_mode():
            raise RuntimeError("Currently bridge is not inactivated")

        if EUDIfNot()(appOutputSize == 0):
            EUDReturn(0)
        EUDEndIf()

        written = EUDVariable()
        if EUDIf()(size >= APP_OUTPUT_MAXSIZE):
            written << APP_OUTPUT_MAXSIZE
        if EUDElse()():
            written << size
        EUDEndIf()

        f_memcpy(appOutputBuffer, src_buffer, written)
        appOutputSize << written

        EUDReturn(written)

    def get_superuser_id(self):
        return self.su_id

    def getWriter(self):
        '''
        Internally printing function uses this method
        '''
        return main.get_main_writer()

    def clean_text(self):
        """Cleans text UI of previous app."""
        EUDIfNot()(main.is_blind_mode())
        f_printf("\n" * 12)
        EUDEndIf()

    @EUDMethod
    def getSTRSectionSize(self):
        return self.payload_size

    def run(self):
        # only super user may interact with apps
        if EUDIf()(Memory(0x512684, Exactly, self.su_id)):
            self.updateMouseState()
            self.updateKeyState()
        EUDEndIf()

        # update current application
        if EUDIfNot()([self.is_terminating_app == 0,
                       self.is_starting_app == 0]):
            self.initOrTerminateApplication()
        EUDEndIf()

        # process all new chats
        prev_text_idx = EUDVariable(initval=10)
        lbl_after_chat = Forward()
        if EUDIf()(Memory(0x640B58, Exactly, prev_text_idx)):
            EUDJump(lbl_after_chat)
        EUDEndIf()

        # parse updated lines
        # since onChat may change text, temporary buffer is required
        db_gametext = Db(13*218+2)
        i = EUDVariable()
        cur_text_idx = f_dwread_epd(EPD(0x640B58))
        f_repmovsd_epd(EPD(db_gametext), EPD(0x640B60), (13*218+2)//4)

        i << prev_text_idx
        chat_off = db_gametext + 218 * i
        if EUDInfLoop()():
            EUDBreakIf(i == cur_text_idx)
            if EUDIf()(f_memcmp(chat_off, self.su_prefix, self.su_prefixlen) == 0):
                self.current_app_instance.onChat(chat_off + self.su_prefixlen)
            EUDEndIf()

            # search next updated lines
            if EUDIf()(i == 10):
                i << 0
                chat_off << db_gametext
            if EUDElse()():
                i += 1
                chat_off += 218
            EUDEndIf()
        EUDEndInfLoop()
        prev_text_idx << cur_text_idx
        lbl_after_chat << NextTrigger()

        # loop
        self.current_app_instance.loop()

        # evaluate display buffer
        if EUDIfNot()(self.update == 0):
            main.get_main_writer().seekepd(EPD(self.display_buffer))

            # print() uses self.writer internally
            self.current_app_instance.print()
            self.update << 0
        EUDEndIf()

        self.current_frame_number += 1
