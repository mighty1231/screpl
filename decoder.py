from eudplib import *
from utils import *
from command import _output_writer

RetDecoderPtr = EUDFuncPtr(1, 0)

@EUDFunc
def ret_DecodeBool(number):
	if EUDIf()(number == 0):
		_output_writer.write_str(makeText('False'))
	if EUDElse()():
		_output_writer.write_str(makeText('True'))
	EUDEndIf()

@EUDFunc
def ret_DecodeBinary(number):
	_output_writer.write_binary(number)

@EUDFunc
def ret_DecodeDecimal(number):
	_output_writer.write_decimal(number)

@EUDFunc
def ret_DecodeHex(number):
	_output_writer.write_hex(number)
