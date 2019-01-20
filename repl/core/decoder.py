from eudplib import *
from ..utils import EPDConstString, EUDByteRW

_output_writer = EUDByteRW()
RetDecoderPtr = EUDFuncPtr(1, 0)

def setOffset(offset):
	_output_writer.seekoffset(offset)

def setEPD(epd):
	_output_writer.seekepd(epd)

@EUDFunc
def _retDecBool(number):
	if EUDIf()(number == 0):
		_output_writer.write_strepd(EPDConstString('False'))
	if EUDElse()():
		_output_writer.write_strepd(EPDConstString('True'))
	EUDEndIf()

@EUDFunc
def _retDecBinary(number):
	_output_writer.write_binary(number)

@EUDFunc
def _retDecDecimal(number):
	_output_writer.write_decimal(number)

@EUDFunc
def _retDecHex(number):
	_output_writer.write_hex(number)

retDecBool = RetDecoderPtr(_retDecBool)
retDecBinary = RetDecoderPtr(_retDecBinary)
retDecDecimal = RetDecoderPtr(_retDecDecimal)
retDecHex = RetDecoderPtr(_retDecHex)
