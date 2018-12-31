from eudplib import *
from utils import *

_output_writer = EUDByteRW()
RetDecoderPtr = EUDFuncPtr(1, 0)

@EUDFunc
def retDecBool(number):
	if EUDIf()(number == 0):
		_output_writer.write_str(makeText('False'))
	if EUDElse()():
		_output_writer.write_str(makeText('True'))
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
