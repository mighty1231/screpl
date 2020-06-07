from eudplib import *

from . import byterw as rw

_buf = Db(4096)
_writer = None

def _get_writer():
    """REPLByteRW instance that used only on this module"""
    global _writer

    if _writer is None:
        _writer = rw.REPLByteRW()
    return _writer

@EUDFunc
def _print_buf():
    # temporarily change string #1 and restore
    if EUDExecuteOnce()():
        _strx_section, _strx_section_epd = f_dwepdread_epd(EPD(0x5993D4))
        _offset_1 = _strx_section_epd + 1
        _buf_offset = _buf - _strx_section
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

def f_raise_error(*args):
    _get_writer().seekepd(EPD(_buf))
    _get_writer().write_f(*args)
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

class DisplayWriter:
    r"""Helps to display text, preserving bottom part of chat

    Usage::

        with DisplayWriter() as writer:
            writer.write_f("Hello\n")
            writer.write_f("Line number 2\n")
            writer.write(0)
    """
    def __init__(self, preserve_chat=True):
        self.preserve_chat = preserve_chat

    def __enter__(self):
        writer = _get_writer()
        writer.seekepd(EPD(_buf))
        self.txt_ptr = f_dwread_epd(EPD(0x640B58))
        return writer

    def __exit__(self, ex_type, ex_val, tb):
        _print_buf()

        if self.preserve_chat:
            SeqCompute([(EPD(0x640B58), SetTo, self.txt_ptr)])
