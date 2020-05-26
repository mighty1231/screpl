from eudplib import *

import screpl.resources.table.tables as tb
from screpl.utils.conststring import EPDConstString
from screpl.utils.referencetable import search_table
from screpl.utils.string import f_strcmp_ptrepd

from .encoder import read_number, read_name, ArgEncoderPtr

tmpbuf = Db(100) # Temporarily store string

def _makeConstEncoder(table):
    @EUDFunc
    def _enc(offset, delim, ref_offset_epd, retval_epd):
        if EUDIf()(read_name(offset, delim, ref_offset_epd, EPD(tmpbuf)) == 1):
            if EUDIf()(search_table(tmpbuf, EPD(table), f_strcmp_ptrepd, retval_epd) == 1):
                EUDReturn(1)
            if EUDElse()():
                f_dwwrite_epd(ref_offset_epd, offset)
                EUDReturn(0)
            EUDEndIf()
        EUDEndIf()
        EUDReturn(read_number(offset, delim, ref_offset_epd, retval_epd))
    return _enc

@EUDFunc
def _EncodeCount(offset, delim, ref_offset_epd, retval_epd):
    if EUDIf()(read_name(offset, delim, ref_offset_epd, EPD(tmpbuf)) == 1):
        if EUDIf()(f_strcmp_ptrepd(tmpbuf, EPDConstString('All')) == 0):
            f_dwwrite_epd(retval_epd, 0)
            EUDReturn(1)
        if EUDElse()():
            f_dwwrite_epd(ref_offset_epd, offset)
            EUDReturn(0)
        EUDEndIf()
    EUDEndIf()
    EUDReturn(read_number(offset, delim, ref_offset_epd, retval_epd))

ArgEncNumber = ArgEncoderPtr(read_number)
ArgEncCount = ArgEncoderPtr(_EncodeCount)
ArgEncModifier = ArgEncoderPtr(_makeConstEncoder(tb.Modifier))
ArgEncAllyStatus = ArgEncoderPtr(_makeConstEncoder(tb.AllyStatus))
ArgEncComparison = ArgEncoderPtr(_makeConstEncoder(tb.Comparison))
ArgEncOrder = ArgEncoderPtr(_makeConstEncoder(tb.Order))
ArgEncPlayer = ArgEncoderPtr(_makeConstEncoder(tb.Player))
ArgEncPropState = ArgEncoderPtr(_makeConstEncoder(tb.PropState))
ArgEncResource = ArgEncoderPtr(_makeConstEncoder(tb.Resource))
ArgEncScore = ArgEncoderPtr(_makeConstEncoder(tb.Score))
ArgEncSwitchAction = ArgEncoderPtr(_makeConstEncoder(tb.SwitchAction))
ArgEncSwitchState = ArgEncoderPtr(_makeConstEncoder(tb.SwitchState))
