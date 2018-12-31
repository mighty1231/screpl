from eudplib import *
from ...core.command import EUDCommandPtr
from ...utils import EUDByteRW, makeEPDText

_writer = EUDByteRW()

@EUDFunc
def decItem_StringDecimal(offset, name, val):
    _writer.seekoffset(offset)
    _writer.write_strepd(name)
    _writer.write_strepd(makeEPDText(': '))
    _writer.write_decimal(val)
    _writer.write(0)

@EUDFunc
def decItem_StringHex(offset, name, val):
    _writer.seekoffset(offset)
    _writer.write_strepd(name)
    _writer.write_strepd(makeEPDText(': '))
    _writer.write_hex(val)
    _writer.write(0)

@EUDFunc
def decItem_String(offset, name, val):
    _writer.seekoffset(offset)
    _writer.write_strepd(name)
    _writer.write(0)

@EUDFunc
def decItem_Command(offset, name, val):
    _writer.seekoffset(offset)
    _writer.write_strepd(name)
    _writer.write_strepd(makeEPDText(" - "))
    _writer.write_strepd(
        EUDCommandPtr.cast(val)._doc_epd)
    _writer.write(0)
