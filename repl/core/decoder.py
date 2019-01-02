from eudplib import *

from ..utils import EUDByteRW, makeEPDText

_output_writer = EUDByteRW()
RetDecoderPtr = EUDFuncPtr(1, 0)

@EUDFunc
def _retDecBool(number):
	if EUDIf()(number == 0):
		_output_writer.write_strepd(makeEPDText('False'))
	if EUDElse()():
		_output_writer.write_strepd(makeEPDText('True'))
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
