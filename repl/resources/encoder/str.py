from eudplib import *
from ...base.encoder import ReadNumber, ReadString, ArgEncoderPtr
from ...base.referencetable import SearchTable
from ..table.tables import (
    tb_AIScript,
    tb_swSub,
    tb_swMap
)
from ...utils import f_strcmp_ptrepd

tmpbuf = Db(150) # Temporarily store string
tmpstrbuf = DBString(150)

@EUDFunc
def _argEncAIScript(offset, delim, ref_offset_epd, retval_epd):
    if EUDIf()(ReadNumber(offset, delim, ref_offset_epd, retval_epd) == 1):
        EUDReturn(1)
    if EUDElseIf()(ReadString(offset, delim, ref_offset_epd, EPD(tmpbuf)) == 1):
        if EUDIf()(SearchTable(tmpbuf, EPD(tb_AIScript), f_strcmp_ptrepd, retval_epd)  == 1):
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

argEncAIScript = ArgEncoderPtr(_argEncAIScript)
argEncSwitch = ArgEncoderPtr(_argEncSwitch)
