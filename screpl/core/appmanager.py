from eudplib import *

from screpl.utils.pool import DbPool, VarPool
from screpl.utils.debug import f_raise_error, f_raise_warning, f_printf
from screpl.utils.keycode import get_key_code
from screpl.utils.string import f_strlen
from screpl.utils.uuencode import uuencode, uudecode

import screpl.main as main

_KEYPRESS_DELAY = 8
_APP_MAX_COUNT = 30

_INTERACT_SIMPLE = 0xEBEBEBEB
_INTERACT_CUSTOM = 0xEEEEEEEE

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
        self._foreground_app_instance = ApplicationInstance(self)
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

        # user interactions
        self._interactive_method = None
        self._allocating_methods = []
        self._simple_interacton_id = 0
        self._binary_buffer = Db(60)
        self._gc_buffer = Db(b'..\x5C\xFF\x14SCR' + b'.' * 77)
        self._recv_funcptr = EUDVariable()
        self._recv_simple_interaction_id = EUDVariable()
        self._human_count = EUDVariable()

        # 64, 96, 128, 192, 256
        # Multiply 32 to get pixel coordinate
        dim = GetChkTokenized().getsection(b'DIM ')
        self.map_width = b2i2(dim, 0)
        self.map_height = b2i2(dim, 2)

    def alloc_variable(self, count):
        return self.varpool.alloc(count)

    def free_variable(self, ptr):
        self.varpool.free(ptr)

    def alloc_db_epd(self, sizequarter):
        """allocate SIZEQUARTER*4 bytes"""
        return self.dbpool.alloc_epd(sizequarter)

    def free_db_epd(self, epd):
        self.dbpool.free_epd(epd)

    def get_foreground_app_instance(self):
        return self._foreground_app_instance

    def start_application(self, app):
        """Queue to start app

        It just records that the app should start. Actual start of the app is
        at the next frame.
        """
        from .application import Application
        assert issubclass(app, Application)

        app.allocate(self)
        self._start_application(len(app._fields_),
                                app._methodarray_,
                                EPD(app._cmdtable_))

    @EUDMethod
    def _start_application(self, fieldsize, methods, table_epd):
        if EUDIfNot()(self.is_terminating_app == 0):
            f_raise_error("Conflict: start_application and request_destruct")
        EUDEndIf()

        if EUDIf()(self.app_cnt < _APP_MAX_COUNT):
            self.app_member_stack[self.app_cnt] = self.alloc_variable(fieldsize)
            self.app_method_stack[self.app_cnt] = methods
            self.app_cmdtab_stack[self.app_cnt] = table_epd
            self.app_cnt += 1

            self.is_starting_app << 1
        if EUDElse()():
            f_raise_warning("APP COUNT reached MAX, No more spaces")
        EUDEndIf()

    def _update_app_stack(self):
        # Terminate one
        if EUDIfNot()(self.is_terminating_app == 0):
            if EUDIf()(self.app_cnt == 1):
                f_raise_error("FATAL ERROR: Excessive TerminateApplication")
            EUDEndIf()

            self._foreground_app_instance.on_destruct()
            self.free_variable(self.cur_members)

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

            self._foreground_app_instance.on_resume()

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

                self._foreground_app_instance.on_init()

                EUDBreakIf(self.cur_app_id >= self.app_cnt - 1)
            EUDEndInfLoop()

            self.is_starting_app << 0
        EUDEndIf()

        self.request_update()

    def push_current_allocating_method(self, method):
        if method.interactive:
            self._interactive_method = method
        self._allocating_methods.append(method)

    def pop_current_allocating_method(self):
        last = self._allocating_methods.pop()
        if last is self._interactive_method:

            self._interactive_method = None
            for method in reversed(self._allocating_methods):
                if method.interactive:
                    self._interactive_method = method
                    break

    @EUDMethod
    def _send_simple_interaction(self, funcptr, id_):
        if EUDIf()(Memory(0x512684, Exactly, self.su_id)):
            f_dwwrite_epd(EPD(self._binary_buffer), funcptr)
            f_dwwrite_epd(EPD(self._binary_buffer)+1, _INTERACT_SIMPLE)
            f_dwwrite_epd(EPD(self._binary_buffer)+2, id_)
            uuencode(self._binary_buffer, 12, EPD(self._gc_buffer) + 2)
            QueueGameCommand(self._gc_buffer + 2, 82)
        EUDEndIf()

    def _update_key_state(self):
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
                    conditions=[
                        prevs[4*i] << MemoryX(0, Exactly, 0, 0xFF * pos),
                        curs[4*i] << MemoryX(0, Exactly, 0, 0xFF * pos)
                    ],
                    actions=[
                        states[4*i] << SetMemory(0x58A364, SetTo, 0)
                    ]
                )
                # 0->1: set 1
                Trigger(
                    conditions=[
                        prevs[4*i+1] << MemoryX(0, Exactly, 0, 0xFF * pos),
                        curs[4*i+1] << MemoryX(0, Exactly, pos, 0xFF * pos)
                    ],
                    actions=[
                        states[4*i+1] << SetMemory(0, SetTo, 1),
                        subs[4*i] << SetMemory(0, SetTo, 1),
                    ]
                )
                # 1->0: set -1
                Trigger(
                    conditions=[
                        prevs[4*i+2] << MemoryX(0, Exactly, pos, 0xFF * pos),
                        curs[4*i+2] << MemoryX(0, Exactly, 0, 0xFF * pos)
                    ],
                    actions=[
                        states[4*i+2] << SetMemory(0, SetTo, 2**32-1),
                        subs[4*i+1] << SetMemory(0, SetTo, 0),
                    ]
                )
                # 1->1: +1
                Trigger(
                    conditions=[
                        prevs[4*i+3] << MemoryX(0, Exactly, pos, 0xFF * pos),
                        curs[4*i+3] << MemoryX(0, Exactly, pos, 0xFF * pos)
                    ],
                    actions=[
                        states[4*i+3] << SetMemory(0, Add, 1),
                        subs[4*i+2] << SetMemory(0, SetTo, 0),
                    ]
                )
                # subs (consecutive keydown)
                Trigger(
                    conditions=[
                        states_cond[2*i] << Memory(0, AtLeast, _KEYPRESS_DELAY),
                        states_cond[2*i+1] << Memory(0, AtMost, 2**31-1)
                    ],
                    actions=[
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

    def _update_mouse_state(self):
        # up   -> up   : 1
        # up   -> down : 2
        # down -> up   : 0
        # down -> down : 3
        for i, c in enumerate([2, 8, 32]): # L, R, M
            for _bef, _cur, _state in [(0, 0, 1),
                                       (0, 1, 2),
                                       (1, 0, 0),
                                       (1, 1, 3)]:
                Trigger(
                    conditions=[
                        self.mouse_prev_state.ExactlyX(c*_bef, c),
                        MemoryX(0x6CDDC0, Exactly, c*_cur, c)
                    ], actions=SetMemoryEPD(EPD(self.mouse_state) + i,
                                              SetTo,
                                              _state)
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

    def key_down(self, key):
        if not self._interactive_method:
            raise RuntimeError(
                "User interactions should be checked under "
                "interactive AppMethods, method:{}"
                .format(self._interactive_method))

        interaction_id = self._interactive_method.register_interaction()

        key = get_key_code(key)
        conditions = [
            Memory(0x68C144, Exactly, 0), # chat status - not chatting
            MemoryEPD(self.keystates + key, Exactly, 1)
        ]
        v_ret_bool = EUDVariable()
        trig_branch, trig_ifthen, trig_else = Forward(), Forward(), Forward()

        if EUDIf()(conditions):
            DoActions(SetNextPtr(trig_branch, trig_ifthen))
            v_ret_bool << 1
        if EUDElse()():
            DoActions(SetNextPtr(trig_branch, trig_else))
            v_ret_bool << 0
        EUDEndIf()

        if EUDIf()(self.is_multiplaying()):
            trig_branch << RawTrigger()
            trig_ifthen << NextTrigger()
            self._send_simple_interaction(
                self._interactive_method.funcptr,
                interaction_id)

            trig_else << NextTrigger()
            v_ret_bool << EUDTernary(
                [self._recv_funcptr == self._interactive_method.funcptr,
                 self._recv_simple_interaction_id == interaction_id])(1)(0)
        EUDEndIf()

        return v_ret_bool == 1

    def key_up(self, key):
        if not self._interactive_method:
            raise RuntimeError(
                "User interactions should be checked under "
                "interactive AppMethods, method:{}"
                .format(self._interactive_method))

        interaction_id = self._interactive_method.register_interaction()

        key = get_key_code(key)
        conditions = [
            Memory(0x68C144, Exactly, 0), # chat status - not chatting
            MemoryEPD(self.keystates + key, Exactly, 2**32-1)
        ]
        v_ret_bool = EUDVariable()
        trig_branch, trig_ifthen, trig_else = Forward(), Forward(), Forward()

        if EUDIf()(conditions):
            DoActions(SetNextPtr(trig_branch, trig_ifthen))
            v_ret_bool << 1
        if EUDElse()():
            DoActions(SetNextPtr(trig_branch, trig_else))
            v_ret_bool << 0
        EUDEndIf()

        if EUDIf()(self.is_multiplaying()):
            trig_branch << RawTrigger()
            trig_ifthen << NextTrigger()
            self._send_simple_interaction(
                self._interactive_method.funcptr,
                interaction_id)

            trig_else << NextTrigger()
            v_ret_bool << EUDTernary(
                [self._recv_funcptr == self._interactive_method.funcptr,
                 self._recv_simple_interaction_id == interaction_id])(1)(0)
        EUDEndIf()

        return v_ret_bool == 1

    def key_press(self, key, hold=None):
        """hold: list of keys, such as LCTRL, LSHIFT, LALT, etc..."""
        if not self._interactive_method:
            raise RuntimeError(
                "User interactions should be checked under "
                "interactive AppMethods, method:{}"
                .format(self._interactive_method))

        interaction_id = self._interactive_method.register_interaction()

        if hold is None:
            hold = []

        key = get_key_code(key)
        conditions = [
            Memory(0x68C144, Exactly, 0), # chat status - not chatting
            MemoryEPD(self.keystates + key, AtLeast, 1),
            MemoryEPD(self.keystates_sub + key, Exactly, 1)
        ]
        for holdkey in hold:
            holdkey = get_key_code(holdkey)
            conditions.append(MemoryEPD(self.keystates + holdkey, AtLeast, 1))
        v_ret_bool = EUDVariable()
        trig_branch, trig_ifthen, trig_else = Forward(), Forward(), Forward()

        if EUDIf()(conditions):
            DoActions(SetNextPtr(trig_branch, trig_ifthen))
            v_ret_bool << 1
        if EUDElse()():
            DoActions(SetNextPtr(trig_branch, trig_else))
            v_ret_bool << 0
        EUDEndIf()

        if EUDIf()(self.is_multiplaying()):
            trig_branch << RawTrigger()
            trig_ifthen << NextTrigger()
            self._send_simple_interaction(
                self._interactive_method.funcptr,
                interaction_id)

            trig_else << NextTrigger()
            v_ret_bool << EUDTernary(
                [self._recv_funcptr == self._interactive_method.funcptr,
                 self._recv_simple_interaction_id == interaction_id])(1)(0)
        EUDEndIf()

        return v_ret_bool == 1

    def mouse_lclick(self):
        return MemoryEPD(EPD(self.mouse_state), Exactly, 0)

    def mouse_lpress(self):
        return MemoryEPD(EPD(self.mouse_state), AtLeast, 2)

    def mouse_rclick(self):
        return MemoryEPD(EPD(self.mouse_state+1), Exactly, 0)

    def mouse_rpress(self):
        return MemoryEPD(EPD(self.mouse_state+1), AtLeast, 2)

    def mouse_mclick(self):
        return MemoryEPD(EPD(self.mouse_state+2), Exactly, 0)

    def mouse_mpress(self):
        return MemoryEPD(EPD(self.mouse_state+2), AtLeast, 2)

    @EUDMethod
    def get_mouse_position(self):
        x, y = self.mouse_pos
        EUDReturn([x, y])

    def get_map_width(self):
        # 64, 96, 128, 192, 256
        # Multiply 32 to get pixel coordinate
        return self.map_width

    def get_map_height(self):
        # 64, 96, 128, 192, 256
        # Multiply 32 to get pixel coordinate
        return self.map_height

    def is_multiplaying(self):
        """If current game have more than two humans, return true,
        otherwise false
        """
        return self._human_count >= 2

    def request_update(self):
        """Request update of the display buffer.

        This should be called under AppMethod or AppCommand
        """
        self.update << 1

    def request_destruct(self):
        """Request destruct of the application self, on foreground

        This should be called under AppMethod or AppCommand. When a single
        app requested start_application, destruction should not be requested
        at the same frame.
        """
        if EUDIfNot()(self.is_starting_app == 0):
            f_raise_error("Conflict: start_application and request_destruct")
        EUDEndIf()
        self.is_terminating_app << 1

    @EUDMethod
    def send_app_output_to_bridge(self, src_buffer, size):
        from screpl.bridge_server.blocks.appoutput import (
            APP_OUTPUT_MAXSIZE,
            appOutputSize,
            appOutputBuffer,
        )
        from screpl.main import is_bridge_mode

        if not is_bridge_mode():
            raise RuntimeError("Currently bridge is not activated")

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

    def run(self, writer):
        # only super user may interact with apps
        if EUDIf()(Memory(0x512684, Exactly, self.su_id)):
            self._update_mouse_state()
            self._update_key_state()
        EUDEndIf()

        # update human count
        self._human_count << 0
        for player_id in range(8):
            if GetPlayerInfo(player_id).typestr == "Human":
                if EUDIf()(f_playerexist(player_id)):
                    self._human_count += 1
                EUDEndIf()

        # update current application
        if EUDIfNot()([self.is_terminating_app == 0,
                       self.is_starting_app == 0]):
            self._update_app_stack()
        EUDEndIf()

        # process all new chats
        prev_text_idx = EUDVariable(initval=10)
        lbl_after_chat = Forward()
        self._recv_simple_interaction_id << 0

        if EUDIf()(Memory(0x640B58, Exactly, prev_text_idx)):
            EUDJump(lbl_after_chat)
        EUDEndIf()
        cur_text_idx = f_dwread_epd(EPD(0x640B58))
        i = EUDVariable()

        # read interactions
        if EUDIf()(self.is_multiplaying()):
            i << prev_text_idx
            chat_off = 0x640B60 + 218 * i
            if EUDInfLoop()():
                EUDBreakIf(i == cur_text_idx)
                if EUDIf()(f_memcmp(chat_off,
                                    Db(b'\x14SCR'),
                                    4) == 0):
                    written = uudecode(chat_off + 4, EPD(self._binary_buffer))
                    if EUDIf()(written >= 8):
                        _method_ptr = f_dwread_epd(EPD(self._binary_buffer))
                        _interact_id = f_dwread_epd(EPD(self._binary_buffer)+1)

                        self._recv_funcptr << _method_ptr
                        if EUDIf()([written >= 12,
                                    _interact_id == _INTERACT_SIMPLE]):
                            self._recv_simple_interaction_id << \
                                f_dwread_epd(EPD(self._binary_buffer)+2)
                        EUDEndIf()
                    EUDEndIf()
                    f_bwrite(chat_off, 0)
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
        EUDEndIf()

        # parse updated lines
        # since on_chat may change text, temporary buffer is required
        db_gametext = Db(13*218+2)
        f_repmovsd_epd(EPD(db_gametext), EPD(0x640B60), (13*218+2)//4)

        i << prev_text_idx
        chat_off = db_gametext + 218 * i
        if EUDInfLoop()():
            EUDBreakIf(i == cur_text_idx)
            if EUDIf()(f_memcmp(chat_off,
                                self.su_prefix,
                                self.su_prefixlen) == 0):
                self._foreground_app_instance.on_chat(chat_off
                                                      + self.su_prefixlen)
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
        self._foreground_app_instance.loop()

        # evaluate display buffer
        if EUDIfNot()(self.update == 0):
            writer.seekepd(EPD(self.display_buffer))

            # print() uses main writer internally
            self._foreground_app_instance.print()
            self.update << 0
        EUDEndIf()
