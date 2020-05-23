from eudplib import *

import screpl.resoucres.table.tables as tb
from screpl.utils.referencetable import SearchTable
from screpl.utils.string import f_strcmp_ptrepd

from .encoder import ReadNumber, ReadString, ArgEncoderPtr

tmpbuf = Db(150) # Temporarily store string
tmpstrbuf = DBString(150)

@EUDFunc
def _ArgEncAIScript(offset, delim, ref_offset_epd, retval_epd):
    if EUDIf()(ReadNumber(offset, delim, ref_offset_epd, retval_epd) == 1):
        EUDReturn(1)
    if EUDElseIf()(ReadString(offset, delim, ref_offset_epd, EPD(tmpbuf)) == 1):
        if EUDIf()(SearchTable(tmpbuf, EPD(tb.AIScript), f_strcmp_ptrepd, retval_epd)  == 1):
            EUDReturn(1)
        EUDEndIf()
    EUDEndIf()
    f_dwwrite_epd(ref_offset_epd, offset)
    EUDReturn(0)

@EUDFunc
def _ArgEncSwitch(offset, delim, ref_offset_epd, retval_epd):
    if EUDIf()(ReadNumber(offset, delim, ref_offset_epd, retval_epd) == 1):
        EUDReturn(1)
    if EUDElseIf()(ReadString(offset, delim, ref_offset_epd, EPD(tmpbuf)) == 1):
        if EUDIf()(SearchTable(tmpbuf, EPD(tb.swMap), f_strcmp_ptrepd, retval_epd)  == 1):
            EUDReturn(1)
        if EUDElseIf()(SearchTable(tmpbuf, EPD(tb.swSub), f_strcmp_ptrepd, retval_epd)  == 1):
            EUDReturn(1)
        EUDEndIf()
    EUDEndIf()
    f_dwwrite_epd(ref_offset_epd, offset)
    EUDReturn(0)

ArgEncAIScript = ArgEncoderPtr(_ArgEncAIScript)
ArgEncSwitch = ArgEncoderPtr(_ArgEncSwitch)
