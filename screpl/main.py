"""Initialize module and run apps"""
from eudplib import *
from eudplib.core.mapdata import IsMapdataInitalized

import screpl.apps.repl as repl
from screpl.bridge_server import bridge
from screpl.core.appcommand import AppCommand
from screpl.core.appmanager import AppManager
from screpl.encoder.const import ArgEncNumber
from screpl.utils.debug import f_printf
from screpl.utils.debug import f_raise_error
from screpl.utils.byterw import REPLByteRW
from screpl.utils.string import f_strlen

_main_writer = REPLByteRW()
_manager = None
_bridge_region = None
_is_blind_mode = None
_trigger_timer = EUDVariable(-1)
_loop_count = EUDVariable(0)

def get_app_manager():
    """Returns the unique :class:`~screpl.core.appmanager.AppManager` instance"""
    assert _manager, "AppManager should be initialized"
    return _manager

def get_main_writer():
    """Returns main writer.

    Main writer is :class:`~screpl.utils.byterw.REPLByteRW` instance that is
    responsible for text UI of :class:`~screpl.core.application.Application` and
    writers in :mod:`screpl.writer`. One can use the returned object for memory
    usage but the one should follow following restriction:

      * It should not bother :meth:`~screpl.core.application.Application.print`.
        It may be used freely on the outside of the method.
    """
    return _main_writer

@EUDFunc
def get_loop_count():
    """Returns counter that measures how much loops are called"""
    return _loop_count

def is_bridge_mode():
    """Returns bool that indicates bridge is active"""
    return _bridge_region is not None

def get_bridge_region():
    return _bridge_region

def is_blind_mode():
    """Returns bool that indicates blind mode is active"""
    if is_bridge_mode():
        return _is_blind_mode == 1
    return False

def set_trigger_timer(timer):
    """Sets trigger timer as given timer"""
    _trigger_timer << timer

def initialize_with_id(su_id):
    """Initialize REPL with configurations, with id-certification.

    Args:
        su_id (int): id of super user, it must ranges from 0 to 7.
    """
    global _manager
    assert not _manager, "AppManager initialized twice"

    # assert the map is already loaded by :mod:`eudplib`
    assert IsMapdataInitalized()
    assert 0 <= su_id <= 7
    print("[SC-REPL] Given super user's id = %d" % su_id)

    # build prefix for super user's chat
    # since game text uses different color code whether some chat is
    # mine or not, it should be differentiated recognizing user player id
    su_prefix = Db(40)
    writer = get_main_writer()
    writer.seekepd(EPD(su_prefix))
    writer.write_f("%S:\x07 ", 0x57EEEB + 36*su_id)
    writer.write(0)
    su_prefixlen = f_strlen(su_prefix)

    _manager = AppManager(su_id, su_prefix, su_prefixlen)
    _initialize_rest()

def initialize_with_name(su_name):
    """Initialize REPL with configurations, with name-certification.

    Args:
        su_name (str): name of super user.
    """
    global _manager
    assert not _manager, "AppManager initialized twice"

    # assert the map is already loaded by :mod:`eudplib`
    assert IsMapdataInitalized()
    print("[SC-REPL] Given super user's name = %s" % su_name)

    # build prefix for super user's chat
    # since game text uses different color code whether some chat is
    # mine or not, it should be differentiated recognizing user player id
    su_id = EUDVariable()
    su_name = su_name.encode('utf-8')
    su_prefix = Db(su_name + bytes([58, 7, 32, 0]))
    su_prefixlen = len(su_name) + 3

    # find superuser id
    name_ptr = EUDVariable(0x57EEEB) # player structure
    if EUDWhile()(name_ptr <= 0x57EEEB + 36*7):
        if EUDIf()(f_strcmp(name_ptr, Db(su_name + b'\0')) == 0):
            EUDBreak()
        EUDEndIf()
        DoActions([
            name_ptr.AddNumber(36),
            su_id.AddNumber(1)
        ])
    EUDEndWhile()
    if EUDIf()(su_id == 8):
        f_raise_error("[SC-REPL] super user '%s' not found" % su_name)
    EUDEndIf()

    _manager = AppManager(su_id, su_prefix, su_prefixlen)
    _initialize_rest()

def _initialize_rest():
    """Initialize SC-REPL after manager initialized"""
    from screpl.writer import writer_init

    writer_init()

    # turbo mode
    repl.REPL.add_command("timer", _cmd_trig_timer)
    repl.REPL.add_command("timerOff", _cmd_trig_timer_off)
    repl.REPL.add_command("turbo", _cmd_turbo)
    repl.REPL.add_command("eudturbo", _cmd_eudturbo)


def set_bridge_mode(bridge_mode):
    """Initialize bridge with specificed mode

    Args:
        bridge_mode (str): string that configures bridge mode.
            It must be one of "off", "on", or "blind".
            * If bridge_mode is "off", do not construct BridgeRegion.
            * For case "on", construct BridgeRegion.
            * For case "blind", construct BridgeRegion, and enable blind mode

    Blind mode supports to send all text UI from REPL apps to bridge client.
    """
    global _bridge_region, _is_blind_mode

    if bridge_mode == "on":
        _bridge_region = bridge.BridgeRegion()
        _is_blind_mode = EUDVariable(0)
    elif bridge_mode == "blind":
        _bridge_region = bridge.BridgeRegion()
        _is_blind_mode = EUDVariable(1)
    else:
        if bridge_mode != "off":
            raise RuntimeError(
                f"Unknown bridge_mode '{bridge_mode}'" + \
                ", expected 'on', 'off', or 'blind'"
            )

    if _bridge_region:
        @AppCommand([])
        def toggle_blind(repl):
            """Toggle blind mode"""
            _is_blind_mode << 1 - _is_blind_mode
        repl.REPL.add_command("blind", toggle_blind)

@AppCommand([ArgEncNumber])
def _cmd_trig_timer(self, timer):
    """Set trigger timer (0x6509A0) as given argument"""
    _trigger_timer << timer
    writer = repl.REPL.get_output_writer()
    writer.write_f("Now trigger timer (0x6509A0) is %D "
                   "(0:eudturbo, 1:turbo)", timer)
    writer.write(0)

@AppCommand([])
def _cmd_trig_timer_off(self):
    """Unset trigger timer"""
    _trigger_timer << -1
    writer = repl.REPL.get_output_writer()
    writer.write_f("Trigger timer unset")
    writer.write(0)

@AppCommand([])
def _cmd_turbo(self):
    """Toggle turbo"""
    writer = repl.REPL.get_output_writer()
    if EUDIf()(_trigger_timer.Exactly(-1)):
        _trigger_timer << 1
        writer.write_f("\x16turbo \x07ON")
    if EUDElse()():
        _trigger_timer << -1
        writer.write_f("\x16turbo \x07OFF")
    EUDEndIf()

@AppCommand([])
def _cmd_eudturbo(self):
    """Toggle eudturbo"""
    writer = repl.REPL.get_output_writer()
    if EUDIf()(_trigger_timer.Exactly(-1)):
        _trigger_timer << 0
        writer.write_f("eudturbo \x07ON")
    if EUDElse()():
        _trigger_timer << -1
        writer.write_f("eudturbo \x04OFF")
    EUDEndIf()

def print_ui():
    """print display buffer from manager

    It temporary saves line counts. If line count is decreased, additionally
    print empty lines
    """
    prev_ln = EUDVariable()
    empty_lines = Db(13)

    text_ptr = f_dwread_epd(EPD(0x640B58))
    f_printf("%E", EPD(_manager.display_buffer))
    cur_ln = f_dwread_epd(EPD(0x640B58)) - text_ptr
    Trigger(
        conditions=cur_ln.AtLeast(0x80000000),
        actions=cur_ln.AddNumber(11),
    )
    Trigger(
        conditions=cur_ln.Exactly(0),
        actions=cur_ln.AddNumber(11),
    )

    # now cur_ln is one of 1, 2, ..., 11
    if EUDIfNot()(prev_ln <= cur_ln):
        diff = prev_ln - cur_ln
        _main_writer.seekepd(EPD(empty_lines))
        if EUDInfLoop()():
            EUDBreakIf(diff == 0)
            _main_writer.write(ord("\n"))
            diff -= 1
        EUDEndInfLoop()
        _main_writer.write(0)
        f_printf("%E", EPD(empty_lines))
    EUDEndIf()
    prev_ln << cur_ln

    SeqCompute([(EPD(0x640B58), SetTo, text_ptr)])

def run():
    """Run main loop of SC-REPL"""
    global _loop_count

    if EUDExecuteOnce()():
        # REPL is the application on the base
        _manager.start_application(repl.REPL, jump=False)
    EUDEndExecuteOnce()

    if EUDIfNot()(_trigger_timer.Exactly(-1)):
        DoActions(SetMemory(0x6509A0, SetTo, _trigger_timer))
    EUDEndIf()

    # app-related things
    _manager.run(get_main_writer())

    # print top of the screen, enables chat simultaneously
    if _bridge_region:
        # in blind mode case, display buffer is managed in BlindModeBlock
        if EUDIf()(_is_blind_mode == 0):
            print_ui()
        EUDEndIf()
        _bridge_region.run()
    else:
        print_ui()

    # update loop count
    _loop_count += 1
