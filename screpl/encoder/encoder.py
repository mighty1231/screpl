from eudplib import *

from screpl.utils import eudbyterw as rw

_reader = rw.EUDByteRW()
_writer = rw.EUDByteRW()

ArgEncoderPtr = EUDFuncPtr(4, 1)

# encode functions
# args
# offset: string to read
# delim: delimiter (encoder reads until the character is met)
# ref_offset_epd: reference for offset. It used for update of offset
# ref_retval_epd: reference for place that returned value is stored
#
# returns 1 if success, otherwise 0

@EUDFunc
def _trim():
    """makes reader skip all spaces"""
    _b = _reader.read()
    if EUDInfLoop()():
        EUDBreakIfNot(_b == ord(' '))
        _b << _reader.read()
    EUDEndInfLoop()
    EUDReturn(_b)

@EUDFunc
def _read_until_delimiter(_b, delim):
    """Moves reader just before specific character.

    It reads zero or more spaces and check the following character.

    Args:
        _b (int): the last character read
        delim (int): the character to be expected after spaces. It may have
            value one of ord(','), ord(')') or 0.

    Returns:
        int: 1 if the last character after spaces is given delim,
            otherwise 0.
    """
    if EUDInfLoop()():
        if EUDIf()(_b == delim):
            EUDReturn(1)
        if EUDElseIfNot()(_b == ord(' ')):
            EUDReturn(0)
        EUDEndIf()
        _b << _reader.read()
    EUDEndInfLoop()

@EUDFunc
def ReadNumber(offset, delim, ref_offset_epd, ref_retval_epd):
    """Reads string and extracts corresponding number.

    It reads following regular expression

        [-]?[1-9][0-9]*
        [-]?0x[0-9A-Fa-f]+

    Args:
        offset (EUDVariable): pointer to string
        delim (int): delimiter character. Reader reads until given character
            is met.
        ref_offset_epd (int): reference for offset. It is used to update offset.
        ref_retval_epd (int): reference for place that returned value is stored.
    """
    _reader.seekoffset(offset)

    # State-related variables
    ret = EUDVariable()
    ret << 0
    sign = EUDVariable()
    sign << 0

    read_delim = Forward()
    failed = Forward()

    _b = _trim()
    if EUDIf()(_b == ord('-')):
        sign << 1
        _b << _reader.read()
    EUDEndIf()
    if EUDIf()(_b == ord('0')):
        _b << _reader.read()

        # Hex
        if EUDIf()(_b == ord('x')):
            _b << _reader.read()
            if EUDIf()([ord('0') <= _b, _b <= ord('9')]):
                ret << ret * 16 + _b - ord('0')
            if EUDElseIf()([ord('a') <= _b, _b <= ord('f')]):
                ret << ret * 16 + _b - (ord('a') - 10)
            if EUDElseIf()([ord('A') <= _b, _b <= ord('F')]):
                ret << ret * 16 + _b - (ord('A') - 10)
            if EUDElse()():
                EUDJump(failed) # At least one character
            EUDEndIf()
            if EUDInfLoop()():
                _b << _reader.read()
                if EUDIf()([ord('0') <= _b, _b <= ord('9')]):
                    ret << ret * 16 + _b - ord('0')
                if EUDElseIf()([ord('a') <= _b, _b <= ord('f')]):
                    ret << ret * 16 + _b - (ord('a') - 10)
                if EUDElseIf()([ord('A') <= _b, _b <= ord('F')]):
                    ret << ret * 16 + _b - (ord('A') - 10)
                if EUDElse()():
                    EUDJump(read_delim)
                EUDEndIf()
            EUDEndInfLoop()
        EUDEndIf()

        # 0
        EUDJump(read_delim)

    # decimal
    if EUDElse()():
        if EUDIf()([ord('0') <= _b, _b <= ord('9')]):
            ret << ret * 10 + _b - ord('0')
        if EUDElse()():
            EUDJump(failed) # At least one character
        EUDEndIf()
        if EUDInfLoop()():
            _b << _reader.read()
            if EUDIf()([ord('0') <= _b, _b <= ord('9')]):
                ret << ret * 10 + _b - ord('0')
            if EUDElse()():
                EUDJump(read_delim)
            EUDEndIf()
        EUDEndInfLoop()
    EUDEndIf()

    # success
    PushTriggerScope()
    read_delim << NextTrigger()
    if EUDIf()(_read_until_delimiter(_b, delim) == 1):
        if EUDIf()(sign == 0):
            f_dwwrite_epd(ref_retval_epd, ret)
        if EUDElse()():
            f_dwwrite_epd(ref_retval_epd, -ret)
        EUDEndIf()
        f_dwwrite_epd(ref_offset_epd, _reader.getoffset())
        EUDReturn(1)
    if EUDElse()():
        EUDJump(failed)
    EUDEndIf()
    PopTriggerScope()

    # error
    failed << NextTrigger()
    EUDReturn(0)

@EUDFunc
def ReadName(offset, delim, ref_offset_epd, ref_retval_epd):
    """Reads string and extracts corresponding symbol

    [_a-zA-Z][_0-9a-zA-Z]*
    ref_retval_epd is pointer for Db
    """
    _reader.seekoffset(offset)

    # result is stored on Db
    _writer.seekepd(ref_retval_epd)

    # State-related variables
    ret = EUDVariable()
    ret << 0

    read_delim = Forward()
    failed = Forward()

    _b = _trim()
    if EUDIf()(EUDOr([_b == ord('_')], [ord('a') <= _b, _b <= ord('z')], [ord('A') <= _b, _b <= ord('Z')])):
        _writer.write(_b)
        if EUDInfLoop()():
            _b << _reader.read()
            if EUDIf()(EUDOr([_b == ord('_')], [ord('a') <= _b, _b <= ord('z')], [ord('A') <= _b, _b <= ord('Z')], \
                    [ord('0') <= _b, _b <= ord('9')])):
                _writer.write(_b)
            if EUDElse()():
                EUDJump(read_delim)
            EUDEndIf()
        EUDEndInfLoop()
    if EUDElse()():
        EUDJump(failed)
    EUDEndIf()

    # success
    PushTriggerScope()
    read_delim << NextTrigger()
    if EUDIf()(_read_until_delimiter(_b, delim) == 1):
        f_dwwrite_epd(ref_offset_epd, _reader.getoffset())
        _writer.write(0)
        EUDReturn(1)
    if EUDElse()():
        EUDJump(failed)
    EUDEndIf()
    PopTriggerScope()

    # error
    failed << NextTrigger()
    EUDReturn(0)

@EUDFunc
def ReadString(offset, delim, ref_offset_epd, ref_retval_epd):
    '''
    "[CHARACTERS]*"
    CHARACTERS : 0x20~0x7E, except for ord('"') = 34
    ref_retval_epd is pointer for Db
    '''
    _reader.seekoffset(offset)

    # result is stored on Db
    _writer.seekepd(ref_retval_epd)

    # State-related variables
    ret = EUDVariable()
    ret << 0

    read_delim = Forward()
    failed = Forward()

    _b = _trim()
    if EUDIf()(_b == ord('"')):
        if EUDInfLoop()():
            _b << _reader.read()
            if EUDIf()(_b == ord('"')): # closing \"
                _b << _reader.read()
                EUDJump(read_delim)
            EUDEndIf()
            if EUDIf()([0x20 <= _b, _b <= 0x7E]):
                _writer.write(_b)
            if EUDElse()():
                EUDJump(failed)
            EUDEndIf()
        EUDEndInfLoop()
    if EUDElse()():
        EUDJump(failed)
    EUDEndIf()

    # success
    PushTriggerScope()
    read_delim << NextTrigger()
    if EUDIf()(_read_until_delimiter(_b, delim) == 1):
        f_dwwrite_epd(ref_offset_epd, _reader.getoffset())
        _writer.write(0)
        EUDReturn(1)
    if EUDElse()():
        EUDJump(failed)
    EUDEndIf()
    PopTriggerScope()

    # error
    failed << NextTrigger()
    EUDReturn(0)

