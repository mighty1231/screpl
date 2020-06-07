from eudplib import *

from screpl.apps.repl import REPL
from screpl.core.appcommand import AppCommand
from screpl.main import get_app_manager
from screpl.main import is_bridge_mode

# initialize variables
app_manager = get_app_manager()

def plugin_get_dependency():
    """Returns list of required plugins"""
    return []

@EUDFunc
def eval_screen_size():
    """evaluate screen size

    Make centerview to center of the map, and evaluate 0x62848C, 0x6284A8
    """
    center_x = 32 // 2 * app_manager.get_map_width()
    center_y = 32 // 2 * app_manager.get_map_height()

    loc1_le = EPD(0x58DC60)
    loc1_te = EPD(0x58DC60 + 4)
    loc1_re = EPD(0x58DC60 + 8)
    loc1_be = EPD(0x58DC60 + 12)

    # screen position and location
    loc1_lv = f_dwread_epd(loc1_le)
    loc1_tv = f_dwread_epd(loc1_te)
    loc1_rv = f_dwread_epd(loc1_re)
    loc1_bv = f_dwread_epd(loc1_be)
    prev_sx = f_dwread_epd(EPD(0x0062848C))
    prev_sy = f_dwread_epd(EPD(0x006284A8))

    # centerview and update x, y
    SeqCompute([
        (loc1_le, SetTo, center_x),
        (loc1_te, SetTo, center_y),
        (loc1_re, SetTo, center_x),
        (loc1_be, SetTo, center_y)])
    f_dwwrite_epd(loc1_le, center_x)
    f_dwwrite_epd(loc1_te, center_y)
    f_dwwrite_epd(loc1_re, center_x)
    f_dwwrite_epd(loc1_be, center_y)
    DoActions(CenterView(1))
    cur_sx = f_dwread_epd(EPD(0x0062848C))
    cur_sy = f_dwread_epd(EPD(0x006284A8))

    # get size
    dx = center_x - cur_sx
    dy = center_y - cur_sy

    # restore screen
    screen_x = prev_sx + dx
    screen_y = prev_sy + dy
    SeqCompute([
        (loc1_le, SetTo, screen_x),
        (loc1_te, SetTo, screen_y),
        (loc1_re, SetTo, screen_x),
        (loc1_be, SetTo, screen_y)])
    DoActions(CenterView(1))

    # restore location
    SeqCompute([
        (loc1_le, SetTo, loc1_lv),
        (loc1_te, SetTo, loc1_tv),
        (loc1_re, SetTo, loc1_rv),
        (loc1_be, SetTo, loc1_bv)])

    EUDReturn([dx*2, dy*2])

def plugin_setup():
    # make commands
    from .incremental import IncrementalDisplayApp
    from .charreport import CharReportApp

    @AppCommand([])
    def start_command1(self):
        """Start IncrementalDisplayApp"""
        app_manager.start_application(IncrementalDisplayApp)
    REPL.add_command('display', start_command1)

    if is_bridge_mode():
        @AppCommand([])
        def start_command2(self):
            """Export character report to bridge. # of characters per line"""
            app_manager.start_application(CharReportApp)
        REPL.add_command('charreport', start_command2)
