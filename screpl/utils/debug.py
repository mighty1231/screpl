from eudplib import *
from .conststring import EPDConstString

_buf = Db(2048)
_writer = None

def _get_writer():
    global _writer
    from screpl.utils.eudbyterw import EUDByteRW

    if _writer is None:
        _writer = EUDByteRW()
    return _writer

@EUDFunc
def _print_buf():
    # temporarily change string #1 and restore
    if EUDExecuteOnce()():
        STRSection, STRSection_epd = f_dwepdread_epd(EPD(0x5993D4))
        _offset_1 = STRSection_epd + 1
        _buf_offset = _buf - STRSection
    EUDEndExecuteOnce()

    prev_offset = f_dwread_epd(_offset_1)
    orig_cp = f_getcurpl()
    f_setcurpl(f_getuserplayerid())
    DoActions([
        SetMemoryEPD(_offset_1, SetTo, _buf_offset),
        DisplayText(1),
        SetMemoryEPD(_offset_1, SetTo, prev_offset)
    ])
    f_setcurpl(orig_cp)

def f_raise_error(txt):
    _get_writer().seekepd(EPD(_buf))
    _get_writer().write_strepd(EPDConstString(txt))
    _get_writer().write(0)
    _print_buf()
    DoActions(SetMemory(0xDEADBEEF ^ 0xFFFFFFFF, SetTo, 0))

def f_raise_warning(*args):
    _get_writer().seekepd(EPD(_buf))
    _get_writer().write_f(*args)
    _get_writer().write(0)
    _print_buf()

def f_printf(*args):
    _get_writer().seekepd(EPD(_buf))
    _get_writer().write_f(*args)
    _get_writer().write(0)
    _print_buf()
