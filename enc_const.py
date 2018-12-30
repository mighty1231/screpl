# This library should be imported during *TriggerExec
# Otherwise, error happens - IndexError: list index out of range 

from eudplib import *
from encoder import ReadNumber, ReadName, ArgEncoderPtr
from table import ReferenceTable, SearchTable
from utils import *
from enc_tables import (
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
        if EUDIf()(f_strcmp2(tmpbuf, makeText('All')) == 0):
            f_dwwrite_epd(retval_epd, 0)
            EUDReturn(1)
        if EUDElse()():
            f_dwwrite_epd(ref_offset_epd, offset)
            EUDReturn(0)
        EUDEndIf()
    EUDEndIf()
    EUDReturn(ReadNumber(offset, delim, ref_offset_epd, retval_epd))

argEncNumber = ReadNumber
argEncCount = _EncodeCount
argEncModifier = _makeConstEncoder(tb_Modifier)
argEncAllyStatus = _makeConstEncoder(tb_AllyStatus)
argEncComparison = _makeConstEncoder(tb_Comparison)
argEncOrder = _makeConstEncoder(tb_Order)
argEncPlayer = _makeConstEncoder(tb_Player)
argEncPropState = _makeConstEncoder(tb_PropState)
argEncResource = _makeConstEncoder(tb_Resource)
argEncScore = _makeConstEncoder(tb_Score)
argEncSwitchAction = _makeConstEncoder(tb_SwitchAction)
argEncSwitchState = _makeConstEncoder(tb_SwitchState)
