from eudplib import *

from ..utils import EUDByteRW, makeEPDText

_output_writer = EUDByteRW()
RetDecoderPtr = EUDFuncPtr(1, 0)

@EUDFunc
def retDecBool(number):
	if EUDIf()(number == 0):
		_output_writer.write_strepd(makeEPDText('False'))
	if EUDElse()():
		_output_writer.write_strepd(makeEPDText('True'))
	EUDEndIf()

@EUDFunc
def retDecBinary(number):
	_output_writer.write_binary(number)

@EUDFunc
def retDecDecimal(number):
	_output_writer.write_decimal(number)

@EUDFunc
def retDecHex(number):
	_output_writer.write_hex(number)
