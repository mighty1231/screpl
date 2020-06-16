from eudplib import *

from screpl.utils.array import create_refarray
from screpl.utils.debug import f_raise_error, f_raise_warning
from screpl.utils.keycode import get_key_code
from screpl.utils.pool import DbPool, VarPool
from screpl.utils.sync import SyncManager

_KEYPRESS_DELAY = 8
_APP_MAX_COUNT = 30

_APP_STATUS_NORMAL = 0
_APP_STATUS_INITIALIZE = 1
_APP_STATUS_DESTRUCTING = 2

class AppManager:
    def __init__(self, su_id, su_prefix, su_prefixlen):
        from .application import ApplicationInstance, ApplicationStruct

        self.su_id = su_id
        self.su_prefix = su_prefix
        self.su_prefixlen = su_prefixlen

        # pool supports for application instances
        self.dbpool = DbPool(300000)
        self.varpool = VarPool(800)

        # variables that support several apps
        self._foreground_app_instance = ApplicationInstance(self)
        app_refarray = create_refarray(ApplicationStruct,
                                       ApplicationStruct.construct)
        self.app_stack = app_refarray.construct(_APP_MAX_COUNT)
        self.app_status = EUDVariable(_APP_STATUS_NORMAL)
        self.foreground_appstruct = ApplicationStruct.construct()
        self.trig_loop_end = Forward()

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
        self.sync_manager = SyncManager(self.su_id, self.is_multiplaying)
        self.human_count = EUDVariable()
        self._interactive_method = None
        self._allocating_methods = []

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

    def start_application(self, app, jump=True):
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
        if jump:
            EUDJump(self.trig_loop_end)

    @EUDMethod
    def _start_application(self, fieldsize, methods, cmdtable_epd):
        new_appstruct = self.app_stack.push_and_getref()

        if EUDIfNot()(new_appstruct == 0):
            new_appstruct.appfields = self.alloc_variable(fieldsize)
            new_appstruct.appmethods = methods
            new_appstruct.cmdtable_epd = cmdtable_epd
            self.foreground_appstruct << new_appstruct

            self.app_status << _APP_STATUS_INITIALIZE
        if EUDElse()():
            f_raise_warning("APP COUNT reached MAX, No more spaces")
        EUDEndIf()

    def _update_app_stack(self):
        if EUDIf()(self.app_status == _APP_STATUS_DESTRUCTING):
            self._foreground_app_instance.on_resume()
            self.request_update()
        if EUDElseIf()(self.app_status == _APP_STATUS_INITIALIZE):
            self._foreground_app_instance.on_init()
            self.request_update()
        EUDEndIf()
        self.app_status << _APP_STATUS_NORMAL

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

        self.mouse_pos[0] << (f_dwread_epd(EPD(0x0062848C))
                              + f_dwread_epd(EPD(0x006CDDC4)))
        self.mouse_pos[1] << (f_dwread_epd(EPD(0x006284A8))
                              + f_dwread_epd(EPD(0x006CDDC8)))


    @EUDMethod
    def get_mouse_position(self):
        """evaluate mouse position

        This can cause desync
        """
        EUDReturn(self.mouse_pos[0], self.mouse_pos[1])

    def synchronize(self, conditions, variables_to_sync=None):
        return self.sync_manager.sync_and_check(
            self._interactive_method,
            conditions,
            sync=variables_to_sync or [])

    def key_down(self, key, sync=None):
        key = get_key_code(key)
        return self.sync_manager.sync_and_check(
            self._interactive_method,
            [(EPD(0x68C144), Exactly, 0),
             (self.keystates + key, Exactly, 1)],
            sync=sync or [])

    def key_up(self, key, sync=None):
        key = get_key_code(key)
        return self.sync_manager.sync_and_check(
            self._interactive_method,
            [(EPD(0x68C144), Exactly, 0),
             (self.keystates + key, Exactly, 2**32-1)],
            sync=sync or [])

    def key_holdcounter(self, key):
        key = get_key_code(key)
        return f_dwread_epd(self.keystates + key)

    def key_press(self, key, hold=None, sync=None):
        """hold: list of keys, such as LCTRL, LSHIFT, LALT, etc..."""
        if not hold:
            hold = []

        key = get_key_code(key)
        condition_pairs = [
            (EPD(0x68C144), Exactly, 0),
            (self.keystates + key, AtLeast, 1),
            (self.keystates_sub + key, Exactly, 1),
        ]
        for holdkey in hold:
            holdkey = get_key_code(holdkey)
            condition_pairs.append((self.keystates + holdkey, AtLeast, 1))
        return self.sync_manager.sync_and_check(
            self._interactive_method, condition_pairs,
            sync=sync or [])

    def mouse_lclick(self, sync=None):
        return self.sync_manager.sync_and_check(
            self._interactive_method,
            [(EPD(self.mouse_state), Exactly, 0)],
            sync=sync or [])

    def mouse_lpress(self, sync=None):
        return self.sync_manager.sync_and_check(
            self._interactive_method,
            [(EPD(self.mouse_state), AtLeast, 2)],
            sync=sync or [])

    def mouse_rclick(self, sync=None):
        return self.sync_manager.sync_and_check(
            self._interactive_method,
            [(EPD(self.mouse_state+1), Exactly, 0)],
            sync=sync or [])

    def mouse_rpress(self, sync=None):
        return self.sync_manager.sync_and_check(
            self._interactive_method,
            [(EPD(self.mouse_state+1), AtLeast, 2)],
            sync=sync or [])

    def mouse_mclick(self, sync=None):
        return self.sync_manager.sync_and_check(
            self._interactive_method,
            [(EPD(self.mouse_state+2), Exactly, 0)],
            sync=sync or [])

    def mouse_mpress(self, sync=None):
        return self.sync_manager.sync_and_check(
            self._interactive_method,
            [(EPD(self.mouse_state+2), AtLeast, 2)],
            sync=sync or [])

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
        return self.human_count >= 2

    def request_update(self):
        """Request update of the display buffer.

        This should be called under AppMethod or AppCommand
        """
        self.update << 1

    @EUDMethod
    def request_destruct(self):
        """Request destruct of the application self, on foreground"""
        self.app_status << _APP_STATUS_DESTRUCTING
        self._foreground_app_instance.on_destruct()
        self.free_variable(self.foreground_appstruct.appfields)

        self.app_stack.pop()
        self.foreground_appstruct << self.app_stack.at(self.app_stack.size-1)
        EUDJump(self.trig_loop_end)

    @EUDMethod
    def send_app_output_to_bridge(self, src_buffer, size):
        from screpl.bridge_server.blocks.appoutput import (
            APP_OUTPUT_MAXSIZE,
            app_output_size,
            app_output_buffer,
        )
        from screpl.main import is_bridge_mode

        if not is_bridge_mode():
            raise RuntimeError("Currently bridge is not activated")

        # only super user may get app output
        if EUDIfNot()(Memory(0x512684, Exactly, self.su_id)):
            EUDReturn(0)
        EUDEndIf()

        if EUDIfNot()(app_output_size == 0):
            EUDReturn(0)
        EUDEndIf()

        written = EUDVariable()
        if EUDIf()(size >= APP_OUTPUT_MAXSIZE):
            written << APP_OUTPUT_MAXSIZE
        if EUDElse()():
            written << size
        EUDEndIf()

        f_memcpy(app_output_buffer, src_buffer, written)
        app_output_size << written

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
        self.human_count << 0
        for player_id in range(8):
            if GetPlayerInfo(player_id).typestr == "Human":
                if EUDIf()(f_playerexist(player_id)):
                    self.human_count += 1
                EUDEndIf()

        # update current application
        self._update_app_stack()

        # process all new chats
        last_text_idx = EUDVariable(initval=10)
        lbl_after_chat = Forward()
        self.sync_manager.clear_recv()

        EUDJumpIf(Memory(0x640B58, Exactly, last_text_idx), lbl_after_chat)
        cur_text_idx = f_dwread_epd(EPD(0x640B58))

        # parse updated lines & sync things
        # since on_chat may change text, temporary buffer is required
        if EUDIf()(self.is_multiplaying()):
            chat_off = 0x640B60 + 218 * last_text_idx
            if EUDInfLoop()():
                EUDBreakIf(last_text_idx == cur_text_idx)

                # check it is synchronizinng message
                self.sync_manager.parse_recv(chat_off)

                # if it is superuser's chat, handle it and send buffer
                if EUDIf()([Memory(0x512684, Exactly, self.su_id),
                            f_memcmp(chat_off,
                                     self.su_prefix,
                                     self.su_prefixlen) == 0]):
                    self.sync_manager.send_chat(chat_off + self.su_prefixlen)
                EUDEndIf()

                # search next updated lines
                if EUDIf()(last_text_idx == 10):
                    last_text_idx << 0
                    chat_off << 0x640B60
                if EUDElse()():
                    last_text_idx += 1
                    chat_off += 218
                EUDEndIf()
            EUDEndInfLoop()

            # recv chat
            if EUDIfNot()(Memory(self.sync_manager.recv_chat_buffer,
                                 Exactly, 0)):
                self._foreground_app_instance.on_chat(
                    self.sync_manager.recv_chat_buffer)
            EUDEndIf()
        if EUDElse()(): # single play
            db_gametext = Db(13*218+2)
            f_repmovsd_epd(EPD(db_gametext), EPD(0x640B60), (13*218+2)//4)
            chat_off = db_gametext + 218 * last_text_idx
            if EUDInfLoop()():
                EUDBreakIf(last_text_idx == cur_text_idx)

                DoActions(last_text_idx.AddNumber(1))
                Trigger(
                    conditions=[last_text_idx == 11],
                    actions=[last_text_idx.SetNumber(0)],
                )
                if EUDIf()(f_memcmp(chat_off,
                                    self.su_prefix,
                                    self.su_prefixlen) == 0):
                    self._foreground_app_instance.on_chat(chat_off
                                                          + self.su_prefixlen)
                EUDEndIf()

                # search next updated lines
                DoActions(chat_off.AddNumber(218))
                Trigger(
                    conditions=[last_text_idx == 0],
                    actions=[chat_off.SetNumber(db_gametext)],
                )
            EUDEndInfLoop()
        EUDEndIf()

        lbl_after_chat << NextTrigger()

        # loop
        self._foreground_app_instance.loop()

        self.trig_loop_end << NextTrigger()
        if EUDIf()([self.app_status == 0, self.update >= 1]):
            # evaluate display buffer
            writer.seekepd(EPD(self.display_buffer))

            # print() uses main writer internally
            self._foreground_app_instance.print()
            self.update << 0
        if EUDElseIfNot()(self.app_status == _APP_STATUS_NORMAL):
            writer.seekepd(EPD(self.display_buffer))
            if EUDIf()(self.app_status == _APP_STATUS_DESTRUCTING):
                writer.write_f("Destructing App...")
            if EUDElse()():
                writer.write_f("Starting App...")
            EUDEndIf()
            writer.write(0)
        EUDEndIf()
