from eudplib import *
from ...core.encoder import ReadNumber, ReadName, ArgEncoderPtr
from ...core.referencetable import SearchTable
from ...utils import EPDConstString, f_strcmp_ptrepd
from ..table.tables import (
    tb_Modifier,
    tb_AllyStatus,
    tb_Comparison,
    tb_Order,
    tb_Player,
    tb_PropState,
    tb_Resource,
    tb_Score,
    tb_SwitchAction,
    tb_SwitchState
)

tmpbuf = Db(100) # Temporarily store string

def _makeConstEncoder(table):
    @EUDFunc
    def _enc(offset, delim, ref_offset_epd, retval_epd):
        if EUDIf()(ReadName(offset, delim, ref_offset_epd, EPD(tmpbuf)) == 1):
            if EUDIf()(SearchTable(tmpbuf, EPD(table), f_strcmp_ptrepd, retval_epd) == 1):
                EUDReturn(1)
            if EUDElse()():
                f_dwwrite_epd(ref_offset_epd, offset)
                EUDReturn(0)
            EUDEndIf()
        EUDEndIf()
        EUDReturn(ReadNumber(offset, delim, ref_offset_epd, retval_epd))
    return _enc

@EUDFunc
def _EncodeCount(offset, delim, ref_offset_epd, retval_epd):
    if EUDIf()(ReadName(offset, delim, ref_offset_epd, EPD(tmpbuf)) == 1):
        if EUDIf()(f_strcmp_ptrepd(tmpbuf, EPDConstString('All')) == 0):
            f_dwwrite_epd(retval_epd, 0)
            EUDReturn(1)
        if EUDElse()():
            f_dwwrite_epd(ref_offset_epd, offset)
            EUDReturn(0)
        EUDEndIf()
    EUDEndIf()
    EUDReturn(ReadNumber(offset, delim, ref_offset_epd, retval_epd))

argEncNumber = ArgEncoderPtr(ReadNumber)
argEncCount = ArgEncoderPtr(_EncodeCount)
argEncModifier = ArgEncoderPtr(_makeConstEncoder(tb_Modifier))
argEncAllyStatus = ArgEncoderPtr(_makeConstEncoder(tb_AllyStatus))
argEncComparison = ArgEncoderPtr(_makeConstEncoder(tb_Comparison))
argEncOrder = ArgEncoderPtr(_makeConstEncoder(tb_Order))
argEncPlayer = ArgEncoderPtr(_makeConstEncoder(tb_Player))
argEncPropState = ArgEncoderPtr(_makeConstEncoder(tb_PropState))
argEncResource = ArgEncoderPtr(_makeConstEncoder(tb_Resource))
argEncScore = ArgEncoderPtr(_makeConstEncoder(tb_Score))
argEncSwitchAction = ArgEncoderPtr(_makeConstEncoder(tb_SwitchAction))
argEncSwitchState = ArgEncoderPtr(_makeConstEncoder(tb_SwitchState))
