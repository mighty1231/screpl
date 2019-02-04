from eudplib import *
from ...core.encoder import ReadNumber, ReadString, ArgEncoderPtr
from ...core.referencetable import SearchTable
from ..table.tables import (
    tb_unit,
    tb_locSub,
    tb_swSub,
    tb_ai,
    tb_unitMap,
    tb_locMap,
    tb_swMap
)
from ...utils import f_strcmp_ptrepd

tmpbuf = Db(150) # Temporarily store string
tmpstrbuf = DBString(150)

@EUDFunc
def _argEncUnit(offset, delim, ref_offset_epd, retval_epd):
    if EUDIf()(ReadNumber(offset, delim, ref_offset_epd, retval_epd) == 1):
        EUDReturn(1)
    if EUDElseIf()(ReadString(offset, delim, ref_offset_epd, EPD(tmpbuf)) == 1):
        if EUDIf()(SearchTable(tmpbuf, EPD(tb_unitMap), f_strcmp_ptrepd, retval_epd) == 1):
            EUDReturn(1)
        if EUDElseIf()(SearchTable(tmpbuf, EPD(tb_unit), f_strcmp_ptrepd, retval_epd) == 1):
            EUDReturn(1)
        EUDEndIf()
    EUDEndIf()
    f_dwwrite_epd(ref_offset_epd, offset)
    EUDReturn(0)

@EUDFunc
def _argEncLocation(offset, delim, ref_offset_epd, retval_epd):
    if EUDIf()(ReadNumber(offset, delim, ref_offset_epd, retval_epd) == 1):
        EUDReturn(1)
    if EUDElseIf()(ReadString(offset, delim, ref_offset_epd, EPD(tmpbuf)) == 1):
        if EUDIf()(SearchTable(tmpbuf, EPD(tb_locMap), f_strcmp_ptrepd, retval_epd) == 1):
            EUDReturn(1)
        if EUDElseIf()(SearchTable(tmpbuf, EPD(tb_locSub), f_strcmp_ptrepd, retval_epd) == 1):
            EUDReturn(1)
        EUDEndIf()
    EUDEndIf()
    f_dwwrite_epd(ref_offset_epd, offset)
    EUDReturn(0)

@EUDFunc
def _argEncAIScript(offset, delim, ref_offset_epd, retval_epd):
    if EUDIf()(ReadNumber(offset, delim, ref_offset_epd, retval_epd) == 1):
        EUDReturn(1)
    if EUDElseIf()(ReadString(offset, delim, ref_offset_epd, EPD(tmpbuf)) == 1):
        if EUDIf()(SearchTable(tmpbuf, EPD(tb_ai), f_strcmp_ptrepd, retval_epd)  == 1):
            EUDReturn(1)
        EUDEndIf()
    EUDEndIf()
    f_dwwrite_epd(ref_offset_epd, offset)
    EUDReturn(0)

@EUDFunc
def _argEncSwitch(offset, delim, ref_offset_epd, retval_epd):
    if EUDIf()(ReadNumber(offset, delim, ref_offset_epd, retval_epd) == 1):
        EUDReturn(1)
    if EUDElseIf()(ReadString(offset, delim, ref_offset_epd, EPD(tmpbuf)) == 1):
        if EUDIf()(SearchTable(tmpbuf, EPD(tb_swMap), f_strcmp_ptrepd, retval_epd)  == 1):
            EUDReturn(1)
        if EUDElseIf()(SearchTable(tmpbuf, EPD(tb_swSub), f_strcmp_ptrepd, retval_epd)  == 1):
            EUDReturn(1)
        EUDEndIf()
    EUDEndIf()
    f_dwwrite_epd(ref_offset_epd, offset)
    EUDReturn(0)

@EUDFunc
def _argEncString(offset, delim, ref_offset_epd, retval_epd):
    if EUDIf()(ReadNumber(offset, delim, ref_offset_epd, retval_epd) == 1):
        EUDReturn(1)
    if EUDElseIf()(ReadString(offset, delim, ref_offset_epd, \
            EPD(tmpstrbuf.GetStringMemoryAddr())) == 1):
        sp = EUDVariable()
        strId = EncodeString("_" * 2048)
        if EUDExecuteOnce()():
            sp << GetMapStringAddr(strId)
        EUDEndExecuteOnce()
        f_strcpy(sp, tmpstrbuf.GetStringMemoryAddr())
        f_dwwrite_epd(retval_epd, strId)
        EUDReturn(1)
    EUDEndIf()
    f_dwwrite_epd(ref_offset_epd, offset)
    EUDReturn(0)

argEncUnit = ArgEncoderPtr(_argEncUnit)
argEncLocation = ArgEncoderPtr(_argEncLocation)
argEncAIScript = ArgEncoderPtr(_argEncAIScript)
argEncSwitch = ArgEncoderPtr(_argEncSwitch)
argEncString = ArgEncoderPtr(_argEncString)
