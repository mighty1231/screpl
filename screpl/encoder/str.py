from eudplib import *

import screpl.resources.table.tables as tb
from screpl.utils.referencetable import search_table
from screpl.utils.string import f_strcmp_ptrepd

from .encoder import read_number, read_string, ArgEncoderPtr

tmpbuf = Db(150) # Temporarily store string
tmpstrbuf = DBString(150)

@EUDFunc
def _ArgEncAIScript(offset, delim, ref_offset_epd, retval_epd):
    if EUDIf()(read_number(offset, delim, ref_offset_epd, retval_epd) == 1):
        EUDReturn(1)
    if EUDElseIf()(read_string(offset, delim, ref_offset_epd, EPD(tmpbuf)) == 1):
        if EUDIf()(search_table(tmpbuf, EPD(tb.AIScript), f_strcmp_ptrepd, retval_epd)  == 1):
            EUDReturn(1)
        EUDEndIf()
    EUDEndIf()
    f_dwwrite_epd(ref_offset_epd, offset)
    EUDReturn(0)

@EUDFunc
def _ArgEncSwitch(offset, delim, ref_offset_epd, retval_epd):
    if EUDIf()(read_number(offset, delim, ref_offset_epd, retval_epd) == 1):
        EUDReturn(1)
    if EUDElseIf()(read_string(offset, delim, ref_offset_epd, EPD(tmpbuf)) == 1):
        if EUDIf()(search_table(tmpbuf, EPD(tb.swMap), f_strcmp_ptrepd, retval_epd)  == 1):
            EUDReturn(1)
        if EUDElseIf()(search_table(tmpbuf, EPD(tb.swSub), f_strcmp_ptrepd, retval_epd)  == 1):
            EUDReturn(1)
        EUDEndIf()
    EUDEndIf()
    f_dwwrite_epd(ref_offset_epd, offset)
    EUDReturn(0)

ArgEncAIScript = ArgEncoderPtr(_ArgEncAIScript)
ArgEncSwitch = ArgEncoderPtr(_ArgEncSwitch)
